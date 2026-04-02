from rest_framework import viewsets
from core.models import WorkflowConfig, TransitionRule
from core.serializers import WorkflowConfigSerializer, TransitionRuleSerializer
from core.permissions import IsAdmin


class WorkflowConfigViewSet(viewsets.ModelViewSet):
    serializer_class = WorkflowConfigSerializer

    def get_queryset(self):
        return WorkflowConfig.objects.filter(
            organization=self.request.user.organization
        ).prefetch_related('transitions')

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdmin()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)


class TransitionRuleViewSet(viewsets.ModelViewSet):
    serializer_class = TransitionRuleSerializer

    def get_queryset(self):
        return TransitionRule.objects.filter(
            workflow__organization=self.request.user.organization
        )

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsAdmin()]
        return super().get_permissions()