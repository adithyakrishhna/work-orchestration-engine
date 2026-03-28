from django.utils import timezone
from core.models import Task, AuditLog


class SLAService:
    """
    Checks all tasks for SLA breaches.
    In production, this would run as a scheduled job (Celery beat).
    For now, we expose it as an API endpoint + management command.
    """

    @staticmethod
    def check_all_sla():
        """Scan all active tasks and flag SLA breaches"""
        now = timezone.now()
        results = {'breached': 0, 'checked': 0}

        # Get all active tasks with a due date
        active_tasks = Task.objects.filter(
            due_date__isnull=False,
            sla_breached=False,
        ).exclude(
            current_state__in=['done', 'cancelled']
        )

        results['checked'] = active_tasks.count()

        for task in active_tasks:
            if now > task.due_date:
                task.sla_breached = True
                task.save()
                results['breached'] += 1

                # Log the breach
                AuditLog.objects.create(
                    task=task,
                    action=AuditLog.ActionType.SLA_BREACHED,
                    performed_by=None,
                    old_value={'due_date': str(task.due_date)},
                    new_value={'breached_at': str(now)},
                    reason='Task exceeded SLA deadline',
                )

        return results

    @staticmethod
    def get_sla_summary(organization):
        """Get SLA stats for an organization"""
        active_tasks = Task.objects.filter(
            organization=organization,
        ).exclude(current_state__in=['done', 'cancelled'])

        total_active = active_tasks.count()
        breached = active_tasks.filter(sla_breached=True).count()
        at_risk = active_tasks.filter(
            sla_breached=False,
            due_date__isnull=False,
            due_date__lte=timezone.now() + timezone.timedelta(hours=24),
        ).count()

        return {
            'total_active': total_active,
            'breached': breached,
            'at_risk': at_risk,
            'healthy': total_active - breached - at_risk,
            'breach_rate': round(breached / total_active * 100, 1) if total_active > 0 else 0,
        }