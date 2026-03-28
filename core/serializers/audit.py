from rest_framework import serializers
from core.models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.username', read_only=True, default=None)

    class Meta:
        model = AuditLog
        fields = (
            'id', 'task', 'action', 'performed_by',
            'performed_by_name', 'old_value', 'new_value',
            'reason', 'timestamp',
        )
        read_only_fields = fields  # Audit logs are immutable