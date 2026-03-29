from rest_framework import serializers
from core.models import Organization


class OrganizationSerializer(serializers.ModelSerializer):
    member_count = serializers.SerializerMethodField()
    team_count = serializers.SerializerMethodField()

    class Meta:
        model = Organization
        fields = (
            'id', 'name', 'slug',
            'allowed_roles', 'allowed_priorities', 'allowed_task_types',
            'member_count', 'team_count',
            'created_at', 'updated_at',
        )
        read_only_fields = ('id', 'created_at', 'updated_at')

    def get_member_count(self, obj):
        return obj.members.count()

    def get_team_count(self, obj):
        return obj.teams.count()