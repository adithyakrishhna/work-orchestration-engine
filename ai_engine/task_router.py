from django.db.models import Avg, F
from core.models import User, Task


class AITaskRouter:
    """
    Intelligently routes tasks to the best-fit engineer.
    Considers: skill match, current workload, past performance.
    """

    @classmethod
    def recommend(cls, task, candidates=None):
        """
        Returns ranked list of recommended assignees for a task.
        """
        org = task.organization

        if candidates is None:
            candidates = User.objects.filter(
                organization=org,
                role__in=['engineer', 'manager'],
            )

        if not candidates.exists():
            return {
                'task_key': task.task_key,
                'task_title': task.title,
                'required_skills': task.tags or [],
                'recommendations': [],
                'reason': 'No eligible engineers found in this organization',
            }

        recommendations = []
        for user in candidates:
            try:
                score_data = cls._score_candidate(user, task)
                recommendations.append(score_data)
            except Exception as e:
                # Don't let one user's scoring failure break the whole thing
                recommendations.append({
                    'user_id': str(user.id),
                    'username': user.username,
                    'skills': user.skills or [],
                    'factors': {
                        'skill_match': 0,
                        'availability': 0,
                        'past_performance': 0,
                    },
                    'total_score': 0,
                    'reasoning': f'{user.username}: scoring error — {str(e)}',
                })

        recommendations.sort(key=lambda x: x['total_score'], reverse=True)

        return {
            'task_key': task.task_key,
            'task_title': task.title,
            'required_skills': task.tags or [],
            'recommendations': recommendations,
        }

    @classmethod
    def auto_assign(cls, task):
        """
        Automatically assign to the top-scored candidate.
        Returns the best user or None.
        """
        result = cls.recommend(task)
        if result['recommendations']:
            best = result['recommendations'][0]
            if best['total_score'] > 0.3:
                try:
                    return User.objects.get(id=best['user_id'])
                except User.DoesNotExist:
                    return None
        return None

    @classmethod
    def _score_candidate(cls, user, task):
        """Score a single candidate for a task"""
        skill_score = cls._skill_match_score(
            user.skills or [], task.tags or []
        )
        workload_score = cls._workload_score(user)
        performance_score = cls._performance_score(user, task)

        total = round(
            skill_score * 0.40 +
            workload_score * 0.30 +
            performance_score * 0.30,
            3
        )

        return {
            'user_id': str(user.id),
            'username': user.username,
            'skills': user.skills or [],
            'factors': {
                'skill_match': round(skill_score, 2),
                'availability': round(workload_score, 2),
                'past_performance': round(performance_score, 2),
            },
            'total_score': total,
            'reasoning': cls._build_reasoning(
                user, skill_score, workload_score, performance_score
            ),
        }

    @classmethod
    def _skill_match_score(cls, user_skills, task_tags):
        """How well do user's skills match task requirements"""
        # Both empty — no signal, return neutral
        if not task_tags and not user_skills:
            return 0.5

        # Task has no tags — can't score skill match, return neutral
        if not task_tags:
            return 0.5

        # User has no skills listed — slight penalty
        if not user_skills:
            return 0.3

        user_skills_lower = [s.lower().strip() for s in user_skills if s]
        task_tags_lower = [t.lower().strip() for t in task_tags if t]

        if not task_tags_lower:
            return 0.5

        matches = sum(1 for tag in task_tags_lower if tag in user_skills_lower)
        return min(matches / len(task_tags_lower), 1.0)

    @classmethod
    def _workload_score(cls, user):
        """Less active tasks = higher availability score"""
        max_tasks = user.max_concurrent_tasks or 5  # Fallback to 5

        active_tasks = user.assigned_tasks.exclude(
            current_state__in=['done', 'cancelled']
        ).count()

        if max_tasks <= 0:
            return 0.5

        utilization = active_tasks / max_tasks
        if utilization >= 1.0:
            return 0
        elif utilization >= 0.8:
            return 0.2
        elif utilization >= 0.6:
            return 0.5
        elif utilization >= 0.3:
            return 0.8
        return 1.0

    @classmethod
    def _performance_score(cls, user, task):
        """How well has this user performed on similar task types"""
        try:
            completed = user.assigned_tasks.filter(
                current_state='done',
                task_type=task.task_type,
            )

            total_completed = completed.count()
            if total_completed == 0:
                return 0.5  # No history, neutral

            breached = completed.filter(sla_breached=True).count()
            compliance_rate = 1 - (breached / total_completed)

            with_resolution = completed.filter(resolved_at__isnull=False)
            if with_resolution.exists():
                avg_resolution = with_resolution.annotate(
                    res_time=F('resolved_at') - F('created_at')
                ).aggregate(avg=Avg('res_time'))

                if avg_resolution['avg']:
                    hours = avg_resolution['avg'].total_seconds() / 3600
                    speed_score = max(0, min(1, 1 - (hours / 100)))
                else:
                    speed_score = 0.5
            else:
                speed_score = 0.5

            return (compliance_rate * 0.6 + speed_score * 0.4)
        except Exception:
            return 0.5

    @classmethod
    def _build_reasoning(cls, user, skill, workload, performance):
        """Generate human-readable reasoning"""
        parts = []

        if skill >= 0.8:
            parts.append("strong skill match")
        elif skill >= 0.5:
            parts.append("partial skill match")
        elif skill >= 0.3:
            parts.append("limited skill overlap")
        else:
            parts.append("no matching skills")

        if workload >= 0.8:
            parts.append("high availability")
        elif workload >= 0.5:
            parts.append("moderate workload")
        elif workload > 0:
            parts.append("heavy workload")
        else:
            parts.append("fully loaded — no capacity")

        if performance >= 0.7:
            parts.append("excellent track record")
        elif performance >= 0.5:
            parts.append("solid track record")
        else:
            parts.append("limited history")

        return f"{user.username}: {', '.join(parts)}"