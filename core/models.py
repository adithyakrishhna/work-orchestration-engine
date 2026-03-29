import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser


class Organization(models.Model):
    """Company or team that uses this system"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, help_text="URL-friendly name, e.g., 'infosys'")

    # Dynamic configuration — each org defines their own
    allowed_roles = models.JSONField(
        default=list,
        blank=True,
        help_text='Roles in this org, e.g., ["admin", "manager", "developer", "qa"]'
    )
    allowed_priorities = models.JSONField(
        default=list,
        blank=True,
        help_text='Priority levels, e.g., ["critical", "high", "medium", "low"]'
    )
    allowed_task_types = models.JSONField(
        default=list,
        blank=True,
        help_text='Task types, e.g., ["bug", "feature", "story", "spike"]'
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Set defaults if empty
        if not self.allowed_roles:
            self.allowed_roles = ['admin', 'manager', 'engineer', 'viewer']
        if not self.allowed_priorities:
            self.allowed_priorities = ['critical', 'high', 'medium', 'low']
        if not self.allowed_task_types:
            self.allowed_task_types = ['bug', 'feature', 'task', 'improvement']
        # Ensure admin role always exists
        if 'admin' not in self.allowed_roles:
            self.allowed_roles.insert(0, 'admin')
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class User(AbstractUser):
    """Custom user model linked to an organization"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='members',
        null=True,
        blank=True,
    )


    role = models.CharField(max_length=50, default='engineer', help_text="Role defined by organization config")

    # Skills for AI-based task routing later
    skills = models.JSONField(default=list, blank=True, help_text="e.g., ['python', 'django', 'devops']")
    max_concurrent_tasks = models.PositiveIntegerField(default=5)

    def __str__(self):
        return f"{self.username} ({self.role})"


class Team(models.Model):
    """Teams within an organization"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='teams')
    lead = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='led_teams')
    members = models.ManyToManyField(User, related_name='teams', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class WorkflowConfig(models.Model):
    """
    Defines the allowed states and transitions for tasks in an org.
    This IS the state machine configuration.
    Example: 'Bug Tracking Workflow', 'Feature Request Workflow'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='workflows')
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    # States stored as JSON list: ["open", "in_progress", "review", "done", "cancelled"]
    allowed_states = models.JSONField(
        default=list,
        help_text='List of allowed states, e.g., ["open", "in_progress", "review", "done"]'
    )
    initial_state = models.CharField(max_length=50, default='open')
    final_states = models.JSONField(
        default=list,
        help_text='States that mark task as complete, e.g., ["done", "cancelled"]'
    )

    def __str__(self):
        return f"{self.name} ({self.organization.name})"


class TransitionRule(models.Model):
    """
    Defines which state transitions are allowed and who can perform them.
    Example: Only managers can move from 'review' -> 'done'
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    workflow = models.ForeignKey(WorkflowConfig, on_delete=models.CASCADE, related_name='transitions')
    from_state = models.CharField(max_length=50)
    to_state = models.CharField(max_length=50)
    allowed_roles = models.JSONField(
        default=list,
        help_text='Roles allowed to perform this transition, e.g., ["admin", "manager"]'
    )

    class Meta:
        unique_together = ('workflow', 'from_state', 'to_state')

    def __str__(self):
        return f"{self.from_state} → {self.to_state} ({self.workflow.name})"


class Task(models.Model):
    """The core work item — this is what everything revolves around"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    # Basic info
    title = models.CharField(max_length=500)
    description = models.TextField(blank=True)
    task_key = models.CharField(max_length=20, unique=True, editable=False, help_text="Auto-generated like PROJ-001")

    # Relationships
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='tasks')
    team = models.ForeignKey(Team, on_delete=models.SET_NULL, null=True, blank=True, related_name='tasks')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_tasks')
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_tasks')
    workflow = models.ForeignKey(WorkflowConfig, on_delete=models.PROTECT, related_name='tasks')

    # State
    current_state = models.CharField(max_length=50, default='open')

    # Priority & Classification
    priority = models.CharField(max_length=50, default='medium', help_text="Priority defined by organization config")
    task_type = models.CharField(max_length=50, default='task', help_text="Task type defined by organization config")
    tags = models.JSONField(default=list, blank=True, help_text='e.g., ["backend", "urgent"]')

    # SLA tracking
    due_date = models.DateTimeField(null=True, blank=True)
    sla_breached = models.BooleanField(default=False)

    # AI-generated fields
    ai_priority_score = models.FloatField(null=True, blank=True, help_text="AI-predicted priority 0.0 to 1.0")
    ai_estimated_hours = models.FloatField(null=True, blank=True, help_text="AI-predicted completion time")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    resolved_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.task_key}: {self.title}"

    def save(self, *args, **kwargs):
        if not self.task_key:
            # Auto-generate task key like "TASK-001"
            last_task = Task.objects.filter(organization=self.organization).order_by('-created_at').first()
            if last_task and last_task.task_key:
                last_num = int(last_task.task_key.split('-')[-1])
                self.task_key = f"{self.organization.slug.upper()[:4]}-{last_num + 1:04d}"
            else:
                self.task_key = f"{self.organization.slug.upper()[:4]}-0001"
        super().save(*args, **kwargs)


class Comment(models.Model):
    """Comments/activity on a task"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Comment by {self.author.username} on {self.task.task_key}"


class AuditLog(models.Model):
    """
    Immutable log of every action in the system.
    This is GOLD for enterprise systems — shows you think about compliance.
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    class ActionType(models.TextChoices):
        CREATED = 'created', 'Created'
        UPDATED = 'updated', 'Updated'
        STATE_CHANGED = 'state_changed', 'State Changed'
        ASSIGNED = 'assigned', 'Assigned'
        COMMENTED = 'commented', 'Commented'
        SLA_BREACHED = 'sla_breached', 'SLA Breached'
        DELETED = 'deleted', 'Deleted'

    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='audit_logs')
    action = models.CharField(max_length=20, choices=ActionType.choices)
    performed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    old_value = models.JSONField(null=True, blank=True, help_text="Previous state/value")
    new_value = models.JSONField(null=True, blank=True, help_text="New state/value")
    reason = models.TextField(blank=True, help_text="Why this change was made")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.action} on {self.task.task_key} by {self.performed_by}"