from rest_framework import serializers
from core.models import Team
from .user import UserSerializer


class TeamSerializer(serializers.ModelSerializer):
    lead_detail = UserSerializer(source='lead', read_only=True)
    member_count = serializers.SerializerMethodField()

    class Meta:
        model = Team
        fields = (
            'id', 'name', 'organization', 'lead', 'lead_detail',
            'members', 'member_count', 'created_at',
        )
        read_only_fields = ('id', 'created_at')

    def get_member_count(self, obj):
        return obj.members.count()