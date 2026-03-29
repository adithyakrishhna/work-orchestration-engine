from rest_framework import serializers
from core.models import Task, Comment
from .user import UserSerializer


class CommentSerializer(serializers.ModelSerializer):
    author_name = serializers.CharField(source='author.username', read_only=True)

    class Meta:
        model = Comment
        fields = ('id', 'task', 'author', 'author_name', 'content', 'created_at')
        read_only_fields = ('id', 'author', 'created_at')


class TaskListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    assigned_to_name = serializers.CharField(source='assigned_to.username', read_only=True, default=None)
    created_by_name = serializers.CharField(source='created_by.username', read_only=True)
    team_name = serializers.CharField(source='team.name', read_only=True, default=None)
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Task
        fields = (
            'id', 'task_key', 'title', 'current_state', 'priority',
            'task_type', 'assigned_to', 'assigned_to_name',
            'created_by_name', 'team', 'team_name',
            'due_date', 'sla_breached',
            'ai_priority_score', 'comment_count', 'created_at',
        )

    def get_comment_count(self, obj):
        return obj.comments.count()

class TaskDetailSerializer(serializers.ModelSerializer):
    """Full serializer for detail/create/update views"""
    assigned_to_detail = UserSerializer(source='assigned_to', read_only=True)
    created_by_detail = UserSerializer(source='created_by', read_only=True)
    comments = CommentSerializer(many=True, read_only=True)

    class Meta:
        model = Task
        fields = (
            'id', 'task_key', 'title', 'description', 'current_state',
            'priority', 'task_type', 'tags',
            'organization', 'team', 'workflow',
            'assigned_to', 'assigned_to_detail',
            'created_by', 'created_by_detail',
            'due_date', 'sla_breached',
            'ai_priority_score', 'ai_estimated_hours',
            'comments', 'created_at', 'updated_at', 'resolved_at',
        )
        read_only_fields = (
            'id', 'task_key', 'current_state', 'created_by',
            'organization',
            'sla_breached', 'ai_priority_score', 'ai_estimated_hours',
            'created_at', 'updated_at', 'resolved_at',
        )
        
    def validate(self, data):
        request = self.context.get('request')
        if request and request.user and request.user.organization:
            org = request.user.organization
            # Validate priority against org config
            if 'priority' in data and org.allowed_priorities:
                if data['priority'] not in org.allowed_priorities:
                    raise serializers.ValidationError({
                        'priority': f"Invalid priority '{data['priority']}'. "
                                    f"Allowed: {org.allowed_priorities}"
                    })
            # Validate task_type against org config
            if 'task_type' in data and org.allowed_task_types:
                if data['task_type'] not in org.allowed_task_types:
                    raise serializers.ValidationError({
                        'task_type': f"Invalid task type '{data['task_type']}'. "
                                     f"Allowed: {org.allowed_task_types}"
                    })
        return data