from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    Organization, User, Team, WorkflowConfig,
    TransitionRule, Task, Comment, AuditLog,
)


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'created_at')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'organization')
    list_filter = ('role', 'organization')
    fieldsets = UserAdmin.fieldsets + (
        ('Work Info', {'fields': ('organization', 'role', 'skills', 'max_concurrent_tasks')}),
    )


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'lead')


@admin.register(WorkflowConfig)
class WorkflowConfigAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'is_default', 'initial_state')


@admin.register(TransitionRule)
class TransitionRuleAdmin(admin.ModelAdmin):
    list_display = ('workflow', 'from_state', 'to_state', 'allowed_roles')


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('task_key', 'title', 'current_state', 'priority', 'assigned_to', 'sla_breached')
    list_filter = ('current_state', 'priority', 'task_type', 'sla_breached')
    search_fields = ('title', 'task_key')
    readonly_fields = ('task_key', 'created_at', 'updated_at')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('task', 'author', 'created_at')


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ('task', 'action', 'performed_by', 'timestamp')
    list_filter = ('action',)
    readonly_fields = ('id', 'task', 'action', 'performed_by', 'old_value', 'new_value', 'timestamp')