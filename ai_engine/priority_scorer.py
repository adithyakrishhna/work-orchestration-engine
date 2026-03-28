from django.utils import timezone


class AIPriorityScorer:
    """
    Rule-based + keyword-weighted priority scoring engine.
    Scores tasks from 0.0 (low) to 1.0 (critical).

    In production, you'd train a model on historical task data.
    This rule-based approach demonstrates the architecture
    and works without training data.
    """

    CRITICAL_KEYWORDS = [
        'crash', 'down', 'outage', 'security', 'breach', 'data loss',
        'production', 'p0', 'critical', 'emergency', 'broken',
        'vulnerability', 'exploit', 'urgent', 'blocked', 'blocker',
    ]
    HIGH_KEYWORDS = [
        'bug', 'error', 'fail', 'broken', 'not working', 'regression',
        'performance', 'slow', 'timeout', 'memory leak', 'p1',
        'customer', 'client', 'deadline', 'important',
    ]
    LOW_KEYWORDS = [
        'nice to have', 'cosmetic', 'typo', 'refactor', 'cleanup',
        'documentation', 'docs', 'minor', 'trivial', 'low priority',
        'enhancement', 'wish', 'someday', 'style', 'formatting',
    ]

    @classmethod
    def score(cls, task):
        """
        Calculate AI priority score for a task.
        Returns dict with score and explanation.
        """
        scores = {}
        # Safely handle None values
        title = task.title or ''
        description = task.description or ''
        text = f"{title} {description}".lower().strip()

        scores['keyword_score'] = cls._keyword_score(text)
        scores['type_score'] = cls._type_score(task.task_type)
        scores['priority_score'] = cls._manual_priority_score(task.priority)
        scores['deadline_score'] = cls._deadline_score(task.due_date)
        scores['age_score'] = cls._age_score(task.created_at)

        total = round(
            scores['keyword_score'] * 0.35 +
            scores['type_score'] * 0.15 +
            scores['priority_score'] * 0.15 +
            scores['deadline_score'] * 0.20 +
            scores['age_score'] * 0.15,
            3
        )

        top_factors = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        explanation = cls._generate_explanation(top_factors, total)

        return {
            'score': min(max(total, 0.0), 1.0),  # Clamp between 0 and 1
            'factors': scores,
            'explanation': explanation,
        }

    @classmethod
    def estimate_hours(cls, task):
        """Estimate completion time based on task characteristics"""
        base_hours = {
            'bug': 4,
            'feature': 16,
            'task': 8,
            'improvement': 12,
        }
        hours = base_hours.get(task.task_type, 8)

        title = task.title or ''
        description = task.description or ''
        text = f"{title} {description}".lower().strip()
        word_count = len(text.split()) if text else 0

        if word_count > 100:
            hours *= 1.5
        elif word_count > 50:
            hours *= 1.2

        priority_multiplier = {
            'critical': 0.5,
            'high': 0.75,
            'medium': 1.0,
            'low': 1.5,
        }
        hours *= priority_multiplier.get(task.priority, 1.0)

        return round(hours, 1)

    @classmethod
    def _keyword_score(cls, text):
        if not text:
            return 0.3

        critical_count = sum(1 for kw in cls.CRITICAL_KEYWORDS if kw in text)
        high_count = sum(1 for kw in cls.HIGH_KEYWORDS if kw in text)
        low_count = sum(1 for kw in cls.LOW_KEYWORDS if kw in text)

        if critical_count >= 2:
            return 1.0
        elif critical_count == 1:
            return 0.85
        elif high_count >= 2:
            return 0.7
        elif high_count == 1:
            return 0.5
        elif low_count >= 1:
            return 0.15
        return 0.3

    @classmethod
    def _type_score(cls, task_type):
        return {
            'bug': 0.8,
            'feature': 0.5,
            'improvement': 0.4,
            'task': 0.3,
        }.get(task_type, 0.3)

    @classmethod
    def _manual_priority_score(cls, priority):
        return {
            'critical': 1.0,
            'high': 0.75,
            'medium': 0.5,
            'low': 0.25,
        }.get(priority, 0.5)

    @classmethod
    def _deadline_score(cls, due_date):
        if not due_date:
            return 0.3

        try:
            now = timezone.now()
            if now > due_date:
                return 1.0

            hours_left = (due_date - now).total_seconds() / 3600
            if hours_left < 8:
                return 0.95
            elif hours_left < 24:
                return 0.8
            elif hours_left < 72:
                return 0.5
            elif hours_left < 168:
                return 0.3
            return 0.1
        except (TypeError, ValueError):
            return 0.3

    @classmethod
    def _age_score(cls, created_at):
        if not created_at:
            return 0.1

        try:
            age_hours = (timezone.now() - created_at).total_seconds() / 3600
            if age_hours > 168:
                return 0.9
            elif age_hours > 72:
                return 0.6
            elif age_hours > 24:
                return 0.3
            return 0.1
        except (TypeError, ValueError):
            return 0.1

    @classmethod
    def _generate_explanation(cls, factors, total):
        if total >= 0.8:
            level = "CRITICAL"
        elif total >= 0.6:
            level = "HIGH"
        elif total >= 0.4:
            level = "MEDIUM"
        else:
            level = "LOW"

        top = factors[0]
        factor_names = {
            'keyword_score': 'urgency keywords detected',
            'type_score': 'task type',
            'priority_score': 'manual priority setting',
            'deadline_score': 'deadline proximity',
            'age_score': 'task age',
        }
        reason = factor_names.get(top[0], top[0])
        return f"AI Priority: {level} — Primary driver: {reason}"