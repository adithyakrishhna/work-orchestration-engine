from django.db.models import Count, Q, Avg, F
from django.utils import timezone
from core.models import Task, User, AuditLog


class DashboardService:
    """Analytics and stats for the organization dashboard"""

    @staticmethod
    def get_overview(organization):
        """High-level task statistics"""
        tasks = Task.objects.filter(organization=organization)
        now = timezone.now()
        last_7_days = now - timezone.timedelta(days=7)

        total = tasks.count()
        by_state = dict(
            tasks.values_list('current_state')
            .annotate(count=Count('id'))
            .values_list('current_state', 'count')
        )
        by_priority = dict(
            tasks.values_list('priority')
            .annotate(count=Count('id'))
            .values_list('priority', 'count')
        )
        by_type = dict(
            tasks.values_list('task_type')
            .annotate(count=Count('id'))
            .values_list('task_type', 'count')
        )

        # Tasks created in last 7 days
        recent_created = tasks.filter(created_at__gte=last_7_days).count()
        # Tasks completed in last 7 days
        recent_completed = tasks.filter(
            resolved_at__gte=last_7_days
        ).count()

        return {
            'total_tasks': total,
            'by_state': by_state,
            'by_priority': by_priority,
            'by_type': by_type,
            'last_7_days': {
                'created': recent_created,
                'completed': recent_completed,
            },
            'unassigned': tasks.filter(
                assigned_to__isnull=True
            ).exclude(
                current_state__in=['done', 'cancelled']
            ).count(),
        }

    @staticmethod
    def get_team_performance(organization):
        """Per-user task stats — useful for workload balancing"""
        users = User.objects.filter(
            organization=organization,
            role__in=['engineer', 'manager'],
        )

        performance = []
        for user in users:
            assigned = Task.objects.filter(
                assigned_to=user,
                organization=organization,
            )
            active = assigned.exclude(current_state__in=['done', 'cancelled']).count()
            completed = assigned.filter(current_state='done').count()
            breached = assigned.filter(sla_breached=True).count()

            # Average resolution time (for completed tasks)
            avg_resolution = assigned.filter(
                resolved_at__isnull=False,
            ).annotate(
                resolution_time=F('resolved_at') - F('created_at')
            ).aggregate(avg=Avg('resolution_time'))

            avg_hours = None
            if avg_resolution['avg']:
                avg_hours = round(avg_resolution['avg'].total_seconds() / 3600, 1)

            performance.append({
                'user_id': str(user.id),
                'username': user.username,
                'role': user.role,
                'active_tasks': active,
                'completed_tasks': completed,
                'sla_breaches': breached,
                'avg_resolution_hours': avg_hours,
                'workload_percentage': round(
                    active / user.max_concurrent_tasks * 100
                ) if user.max_concurrent_tasks > 0 else 0,
            })

        return sorted(performance, key=lambda x: x['active_tasks'], reverse=True)

    @staticmethod
    def get_recent_activity(organization, limit=20):
        """Recent audit log entries for activity feed"""
        logs = AuditLog.objects.filter(
            task__organization=organization
        ).select_related('performed_by', 'task')[:limit]

        return [
            {
                'task_key': log.task.task_key,
                'task_title': log.task.title,
                'action': log.action,
                'performed_by': log.performed_by.username if log.performed_by else 'System',
                'old_value': log.old_value,
                'new_value': log.new_value,
                'reason': log.reason,
                'timestamp': log.timestamp.isoformat(),
            }
            for log in logs
        ]