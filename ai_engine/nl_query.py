import re
from django.db.models import Q
from core.models import Task


class NLQueryEngine:
    """
    Converts natural language questions into database queries.
    Example: 'show me all critical bugs assigned to alice'
    → Task.objects.filter(priority='critical', task_type='bug', assigned_to__username='alice')
    """

    # Mapping natural language to field values
    # Using tuples (pattern, value) for regex word-boundary matching
    STATE_PATTERNS = [
        (r'\bin[_\s]progress\b', 'in_progress'),
        (r'\bin[_\s]review\b', 'review'),
        (r'\bopen\b', 'open'),
        (r'\bworking\s+on\b', 'in_progress'),
        (r'\breview\b', 'review'),
        (r'\btesting\b', 'testing'),
        (r'\bqa\b', 'testing'),
        (r'\bdone\b', 'done'),
        (r'\bcompleted\b', 'done'),
        (r'\bfinished\b', 'done'),
        (r'\bclosed\b', 'done'),
        (r'\bresolved\b', 'done'),
        (r'\bcancelled\b', 'cancelled'),
        (r'\bcanceled\b', 'cancelled'),
    ]

    PRIORITY_PATTERNS = [
        (r'\bcritical\b', 'critical'),
        (r'\bp0\b', 'critical'),
        (r'\burgent\b', 'critical'),
        (r'\bhigh\s*priority\b', 'high'),
        (r'\bhigh\b', 'high'),
        (r'\bp1\b', 'high'),
        (r'\bmedium\s*priority\b', 'medium'),
        (r'\bmedium\b', 'medium'),
        (r'\bp2\b', 'medium'),
        (r'\blow\s*priority\b', 'low'),
        (r'\blow\b', 'low'),
        (r'\bp3\b', 'low'),
        (r'\bminor\b', 'low'),
    ]

    TYPE_PATTERNS = [
        (r'\bbugs?\b', 'bug'),
        (r'\bdefects?\b', 'bug'),
        (r'\bissues?\b', 'bug'),
        (r'\bfeatures?\b', 'feature'),
        (r'\bimprovements?\b', 'improvement'),
        (r'\benhancements?\b', 'improvement'),
    ]

    # Words that should NOT trigger type matching when used casually
    CASUAL_PHRASES_TO_SKIP = [
        r'i have an issue',
        r'there is an issue',
        r'the issue is',
        r'no issue',
        r'feature of',
    ]

    @classmethod
    def query(cls, text, organization):
        """
        Parse natural language and return matching tasks.
        Returns dict with parsed filters, query explanation, and results.
        """
        text_lower = text.lower().strip()
        filters = Q(organization=organization)
        applied_filters = {}

        # Detect state
        state = cls._match_pattern(cls.STATE_PATTERNS, text_lower)
        if state:
            filters &= Q(current_state=state)
            applied_filters['state'] = state

        # Detect priority
        priority = cls._match_pattern(cls.PRIORITY_PATTERNS, text_lower)
        if priority:
            filters &= Q(priority=priority)
            applied_filters['priority'] = priority

        # Detect type (but skip if used casually)
        if not cls._is_casual_usage(text_lower):
            task_type = cls._match_pattern(cls.TYPE_PATTERNS, text_lower)
            if task_type:
                filters &= Q(task_type=task_type)
                applied_filters['type'] = task_type

        # Detect assignment — look for specific patterns only
        assigned_match = re.search(
            r'(?:assigned\s+to|assignee\s+is|owned\s+by)\s+(\w+)',
            text_lower
        )
        if assigned_match:
            username = assigned_match.group(1)
            filters &= Q(assigned_to__username__icontains=username)
            applied_filters['assigned_to'] = username

        # Detect "created by"
        created_match = re.search(
            r'(?:created\s+by|reported\s+by|filed\s+by|opened\s+by)\s+(\w+)',
            text_lower
        )
        if created_match:
            username = created_match.group(1)
            filters &= Q(created_by__username__icontains=username)
            applied_filters['created_by'] = username

        # Detect unassigned
        if re.search(r'\bunassigned\b|\bnot\s+assigned\b', text_lower):
            filters &= Q(assigned_to__isnull=True)
            applied_filters['unassigned'] = True

        # Detect overdue / breached
        if re.search(r'\boverdue\b|\bbreached\b|\bsla\b|\blate\b|\bmissed\s+deadline\b', text_lower):
            filters &= Q(sla_breached=True)
            applied_filters['sla_breached'] = True

        # Detect team
        team_match = re.search(
            r'(?:team|group)\s+["\']?(\w+(?:\s+\w+)?)["\']?',
            text_lower
        )
        if team_match:
            team_name = team_match.group(1)
            # Don't match "team performance" or "team members" as team names
            skip_words = ['performance', 'members', 'lead', 'stats', 'report']
            if team_name not in skip_words:
                filters &= Q(team__name__icontains=team_name)
                applied_filters['team'] = team_name

        # Detect tag/label search
        tag_match = re.search(
            r'(?:tagged?\s+(?:with|as)?|labeled?|label)\s+["\']?(\w+)["\']?',
            text_lower
        )
        if tag_match:
            tag = tag_match.group(1)
            filters &= Q(tags__contains=[tag])
            applied_filters['tag'] = tag

        # Detect "my tasks" — tasks assigned to current user
        if re.search(r'\bmy\s+tasks?\b|\bassigned\s+to\s+me\b', text_lower):
            # This needs request context, so we flag it
            applied_filters['my_tasks'] = True

        # Execute query
        tasks = Task.objects.filter(filters).select_related(
            'assigned_to', 'created_by', 'team'
        ).order_by('-created_at')[:50]

        # Build explanation
        explanation = cls._build_explanation(applied_filters, tasks.count())

        results = [
            {
                'task_key': t.task_key,
                'title': t.title,
                'state': t.current_state,
                'priority': t.priority,
                'type': t.task_type,
                'assigned_to': t.assigned_to.username if t.assigned_to else None,
                'sla_breached': t.sla_breached,
                'created_at': t.created_at.isoformat(),
            }
            for t in tasks
        ]

        return {
            'query': text,
            'parsed_filters': applied_filters,
            'explanation': explanation,
            'count': len(results),
            'results': results,
        }

    @classmethod
    def _match_pattern(cls, patterns, text):
        """Match first regex pattern that hits"""
        for pattern, value in patterns:
            if re.search(pattern, text):
                return value
        return None

    @classmethod
    def _is_casual_usage(cls, text):
        """Check if type-related words are used casually, not as filters"""
        for pattern in cls.CASUAL_PHRASES_TO_SKIP:
            if re.search(pattern, text):
                return True
        return False

    @classmethod
    def _build_explanation(cls, filters, count):
        parts = []
        if 'state' in filters:
            parts.append(f"state is '{filters['state']}'")
        if 'priority' in filters:
            parts.append(f"priority is '{filters['priority']}'")
        if 'type' in filters:
            parts.append(f"type is '{filters['type']}'")
        if 'assigned_to' in filters:
            parts.append(f"assigned to '{filters['assigned_to']}'")
        if 'created_by' in filters:
            parts.append(f"created by '{filters['created_by']}'")
        if 'unassigned' in filters:
            parts.append("unassigned")
        if 'sla_breached' in filters:
            parts.append("SLA breached")
        if 'team' in filters:
            parts.append(f"in team '{filters['team']}'")
        if 'tag' in filters:
            parts.append(f"tagged '{filters['tag']}'")
        if 'my_tasks' in filters:
            parts.append("assigned to you")

        if parts:
            filter_str = " AND ".join(parts)
            return f"Found {count} tasks where {filter_str}"
        return f"Found {count} tasks (no specific filters detected — showing all)"