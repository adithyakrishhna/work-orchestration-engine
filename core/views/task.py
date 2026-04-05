from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.permissions.rbac import IsAdmin, IsNotViewer
from django_filters.rest_framework import DjangoFilterBackend
from core.models import Task, Comment, AuditLog, User
from core.serializers import (
    TaskListSerializer, TaskDetailSerializer, CommentSerializer,
)
from core.permissions import TaskPermission
from core.permissions.rbac import IsNotViewer
from core.services import StateMachineService



class TaskViewSet(viewsets.ModelViewSet):
    permission_classes = [TaskPermission]

    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsNotViewer()]
        if self.action == 'destroy':
            return [IsAuthenticated(), IsAdmin()]
        return [IsAuthenticated()]

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
        # Set initial state from workflow
        task.current_state = task.workflow.initial_state
        task.save()
        # Create audit log
        AuditLog.objects.create(
            task=task,
            action=AuditLog.ActionType.CREATED,
            performed_by=self.request.user,
            new_value={'title': task.title, 'state': task.current_state},
        )
    


    @action(detail=True, methods=['post'], url_path='transition')
    def transition(self, request, pk=None):
        """
        POST /api/v1/tasks/{id}/transition/
        Body: {"to_state": "in_progress", "reason": "Starting work"}
        """
        task = self.get_object()
        to_state = request.data.get('to_state')
        reason = request.data.get('reason', '')

        if not to_state:
            return Response(
                {'error': 'to_state is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        task = StateMachineService.transition(task, to_state, request.user, reason)
        serializer = TaskDetailSerializer(task)
        return Response(serializer.data)

    @action(detail=True, methods=['get'], url_path='available-transitions')
    def available_transitions(self, request, pk=None):
        """
        GET /api/v1/tasks/{id}/available-transitions/
        Returns what states this user can move the task to.
        """
        task = self.get_object()
        transitions = StateMachineService.get_available_transitions(task, request.user)
        return Response({
            'current_state': task.current_state,
            'available_transitions': transitions,
        })

    @action(detail=True, methods=['post'], url_path='assign')
    def assign(self, request, pk=None):
        """
        POST /api/v1/tasks/{id}/assign/
        Body: {"user_id": "uuid-here", "reason": "Best fit for this task"}
        """
        task = self.get_object()
        user_id = request.data.get('user_id')
        reason = request.data.get('reason', '')

        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            assignee = User.objects.get(id=user_id)
        except User.DoesNotExist:
            return Response(
                {'error': 'User not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        task = StateMachineService.assign_task(task, assignee, request.user, reason)
        serializer = TaskDetailSerializer(task)
        return Response(serializer.data)


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
    
    def get_permissions(self):
        if self.action == 'create':
            return [IsAuthenticated(), IsNotViewer()]
        return [IsAuthenticated()]