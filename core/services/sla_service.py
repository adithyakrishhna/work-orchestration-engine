from django.utils import timezone
from core.models import Task, AuditLog


class SLAService:
    """
    Checks all tasks for SLA breaches.
    In production, this would run as a scheduled job (Celery beat).
    For now, we expose it as an API endpoint + management command.
    """

    @staticmethod
    def check_all_sla(organization=None):
        """Scan all active tasks and flag SLA breaches"""
        now = timezone.now()
        results = {'breached': 0, 'checked': 0, 'breached_tasks': [], 'at_risk_tasks': []}

        # Get all active tasks with a due date
        # Get final states dynamically from workflows
        from core.models import WorkflowConfig
        final_states = set()
        for wf in WorkflowConfig.objects.all():
            final_states.update(wf.final_states or [])
        if not final_states:
            final_states = {'done', 'cancelled'}

        qs = Task.objects.filter(due_date__isnull=False)
        if organization:
            qs = qs.filter(organization=organization)
        active_tasks = qs.exclude(
            current_state__in=list(final_states)
        ).select_related('assigned_to')

        results['checked'] = active_tasks.count()

        # Reset tasks that are no longer breached (due date changed to future or removed)
        previously_breached = Task.objects.filter(
            sla_breached=True,
        )
        if organization:
            previously_breached = previously_breached.filter(organization=organization)
        
        for task in previously_breached:
            if task.due_date is None or now <= task.due_date:
                task.sla_breached = False
                task.save()

        for task in active_tasks:
            if now > task.due_date:
                # Newly breached
                if not task.sla_breached:
                    task.sla_breached = True
                    task.save()
                    AuditLog.objects.create(
                        task=task,
                        action=AuditLog.ActionType.SLA_BREACHED,
                        performed_by=None,
                        old_value={'due_date': str(task.due_date)},
                        new_value={'breached_at': str(now)},
                        reason='Task exceeded SLA deadline',
                    )

                results['breached'] += 1
                results['breached_tasks'].append({
                    'id': str(task.id),
                    'task_key': task.task_key,
                    'title': task.title,
                    'priority': task.priority,
                    'assigned_to': task.assigned_to.username if task.assigned_to else 'Unassigned',
                    'due_date': task.due_date.isoformat(),
                    'hours_overdue': round((now - task.due_date).total_seconds() / 3600, 1),
                })
            else:
                # Check if at risk (less than 24 hours remaining)
                hours_left = (task.due_date - now).total_seconds() / 3600
                if hours_left <= 24:
                    results['at_risk_tasks'].append({
                        'id': str(task.id),
                        'task_key': task.task_key,
                        'title': task.title,
                        'priority': task.priority,
                        'assigned_to': task.assigned_to.username if task.assigned_to else 'Unassigned',
                        'due_date': task.due_date.isoformat(),
                        'hours_remaining': round(hours_left, 1),
                    })

        return results

    @staticmethod
    def get_sla_summary(organization):
        """Get SLA stats for an organization"""
        from core.models import WorkflowConfig
        final_states = set()
        for wf in WorkflowConfig.objects.filter(organization=organization):
            final_states.update(wf.final_states or [])
        if not final_states:
            final_states = {'done', 'cancelled'}

        active_tasks = Task.objects.filter(
            organization=organization,
        ).exclude(current_state__in=list(final_states))

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