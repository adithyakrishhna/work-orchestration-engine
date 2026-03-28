from rest_framework import serializers
from core.models import WorkflowConfig, TransitionRule


class TransitionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransitionRule
        fields = ('id', 'workflow', 'from_state', 'to_state', 'allowed_roles')
        read_only_fields = ('id',)


class WorkflowConfigSerializer(serializers.ModelSerializer):
    transitions = TransitionRuleSerializer(many=True, read_only=True)

    class Meta:
        model = WorkflowConfig
        fields = (
            'id', 'name', 'organization', 'is_default',
            'allowed_states', 'initial_state', 'final_states',
            'transitions', 'created_at',
        )
        read_only_fields = ('id', 'created_at')