from rest_framework import serializers
from core.models import WorkflowConfig, TransitionRule


class TransitionRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransitionRule
        fields = ('id', 'workflow', 'from_state', 'to_state', 'allowed_roles')
        read_only_fields = ('id',)

    def validate(self, data):
        workflow = data.get('workflow')
        from_state = data.get('from_state')
        to_state = data.get('to_state')

        if workflow:
            allowed = workflow.allowed_states
            if from_state and from_state not in allowed:
                raise serializers.ValidationError({
                    'from_state': f"State '{from_state}' does not exist in workflow '{workflow.name}'. "
                                  f"Allowed states: {allowed}"
                })
            if to_state and to_state not in allowed:
                raise serializers.ValidationError({
                    'to_state': f"State '{to_state}' does not exist in workflow '{workflow.name}'. "
                                f"Allowed states: {allowed}"
                })
            if from_state == to_state:
                raise serializers.ValidationError(
                    "from_state and to_state cannot be the same."
                )

        return data


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

    def validate(self, data):
        allowed_states = data.get('allowed_states', [])
        initial_state = data.get('initial_state', '')
        final_states = data.get('final_states', [])

        if allowed_states:
            if initial_state and initial_state not in allowed_states:
                raise serializers.ValidationError({
                    'initial_state': f"Initial state '{initial_state}' must be in allowed_states: {allowed_states}"
                })
            for fs in final_states:
                if fs not in allowed_states:
                    raise serializers.ValidationError({
                        'final_states': f"Final state '{fs}' must be in allowed_states: {allowed_states}"
                    })

        return data