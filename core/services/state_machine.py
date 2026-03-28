from django.utils import timezone
from rest_framework.exceptions import ValidationError
from core.models import AuditLog, TransitionRule


class StateMachineService:
    """
    Enforces workflow transitions with business rules.
    This is the core engine — no state change happens without going through here.
    """

    @staticmethod
    def get_available_transitions(task, user):
        """
        Returns list of states this user can move the task to,
        based on current state + user's role + workflow rules.
        """
        transitions = TransitionRule.objects.filter(
            workflow=task.workflow,
            from_state=task.current_state,
        )

        available = []
        for transition in transitions:
            if user.role in transition.allowed_roles:
                available.append({
                    'to_state': transition.to_state,
                    'allowed_roles': transition.allowed_roles,
                })
        return available

    @staticmethod
    def transition(task, to_state, user, reason=''):
        """
        Attempt to transition a task to a new state.
        Validates everything before allowing the change.
        """
        old_state = task.current_state
        workflow = task.workflow

        # Rule 1: Can't transition to same state
        if old_state == to_state:
            raise ValidationError(f"Task is already in '{old_state}' state.")

        # Rule 2: Target state must exist in workflow
        if to_state not in workflow.allowed_states:
            raise ValidationError(
                f"State '{to_state}' is not valid for workflow '{workflow.name}'. "
                f"Allowed states: {workflow.allowed_states}"
            )

        # Rule 3: Check if this specific transition is allowed
        transition_rule = TransitionRule.objects.filter(
            workflow=workflow,
            from_state=old_state,
            to_state=to_state,
        ).first()

        if not transition_rule:
            raise ValidationError(
                f"Transition from '{old_state}' to '{to_state}' is not allowed "
                f"in workflow '{workflow.name}'."
            )

        # Rule 4: Check if user's role is allowed to perform this transition
        if user.role not in transition_rule.allowed_roles:
            raise ValidationError(
                f"Your role '{user.role}' cannot transition from "
                f"'{old_state}' to '{to_state}'. "
                f"Allowed roles: {transition_rule.allowed_roles}"
            )

        # Rule 5: Task must be assigned before moving to in_progress
        if to_state == 'in_progress' and not task.assigned_to:
            raise ValidationError(
                "Task must be assigned to someone before moving to 'in_progress'."
            )

        # All validations passed — perform the transition
        task.current_state = to_state

        # If moving to a final state, record resolution time
        if to_state in workflow.final_states:
            task.resolved_at = timezone.now()

        task.save()

        # Create audit log
        AuditLog.objects.create(
            task=task,
            action=AuditLog.ActionType.STATE_CHANGED,
            performed_by=user,
            old_value={'state': old_state},
            new_value={'state': to_state},
            reason=reason,
        )

        return task

    @staticmethod
    def assign_task(task, assignee, user, reason=''):
        """Handle task assignment with audit logging"""
        old_assignee = task.assigned_to

        # Validate assignee is in same org
        if assignee.organization != task.organization:
            raise ValidationError("Cannot assign task to user from different organization.")

        # Check assignee workload
        active_tasks = assignee.assigned_tasks.exclude(
            current_state__in=task.workflow.final_states
        ).count()

        if active_tasks >= assignee.max_concurrent_tasks:
            raise ValidationError(
                f"{assignee.username} already has {active_tasks} active tasks "
                f"(max: {assignee.max_concurrent_tasks})."
            )

        task.assigned_to = assignee
        task.save()

        # Audit log
        AuditLog.objects.create(
            task=task,
            action=AuditLog.ActionType.ASSIGNED,
            performed_by=user,
            old_value={'assigned_to': str(old_assignee.id) if old_assignee else None},
            new_value={'assigned_to': str(assignee.id), 'username': assignee.username},
            reason=reason,
        )

        return task