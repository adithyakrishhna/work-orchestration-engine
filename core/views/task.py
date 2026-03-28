from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Task, Comment, AuditLog
from core.serializers import TaskListSerializer, TaskDetailSerializer, CommentSerializer
from core.permissions import TaskPermission


class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [TaskPermission]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['current_state', 'priority', 'task_type', 'assigned_to', 'team', 'sla_breached']
    search_fields = ['title', 'description', 'task_key']
    ordering_fields = ['created_at', 'updated_at', 'priority', 'due_date', 'ai_priority_score']

    def get_serializer_class(self):
        if self.action == 'list':
            return TaskListSerializer
        return TaskDetailSerializer

    def get_queryset(self):
        return Task.objects.filter(
            organization=self.request.user.organization
        ).select_related('assigned_to', 'created_by', 'team', 'workflow')

    def perform_create(self, serializer):
        task = serializer.save(
            created_by=self.request.user,
            organization=self.request.user.organization,
        )
        # Create audit log
        AuditLog.objects.create(
            task=task,
            action=AuditLog.ActionType.CREATED,
            performed_by=self.request.user,
            new_value={'title': task.title, 'state': task.current_state},
        )


class CommentViewSet(viewsets.ModelViewSet):
    serializer_class = CommentSerializer

    def get_queryset(self):
        return Comment.objects.filter(
            task__organization=self.request.user.organization
        )

    def perform_create(self, serializer):
        comment = serializer.save(author=self.request.user)
        # Audit log for comment
        AuditLog.objects.create(
            task=comment.task,
            action=AuditLog.ActionType.COMMENTED,
            performed_by=self.request.user,
            new_value={'comment': comment.content},
        )