from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import AuditLog
from core.serializers import AuditLogSerializer


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    """Audit logs are read-only — nobody can modify history"""
    serializer_class = AuditLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['task', 'action', 'performed_by']

    def get_queryset(self):
        return AuditLog.objects.filter(
            task__organization=self.request.user.organization
        ).select_related('performed_by', 'task')