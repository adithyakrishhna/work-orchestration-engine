from rest_framework import serializers
from core.models import User


class UserSerializer(serializers.ModelSerializer):
    active_task_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'role', 'organization',
            'skills', 'max_concurrent_tasks', 'active_task_count',
        )
        read_only_fields = ('id',)

    def get_active_task_count(self, obj):
        return obj.assigned_tasks.exclude(
            current_state__in=['done', 'cancelled']
        ).count()


class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'password', 'role', 'organization', 'skills')
        read_only_fields = ('id',)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = User(**validated_data)
        user.set_password(password)
        user.save()
        return user
    
    def validate_role(self, value):
        request = self.context.get('request')
        if request and request.user and request.user.organization:
            org = request.user.organization
            if org.allowed_roles and value not in org.allowed_roles:
                raise serializers.ValidationError(
                    f"Invalid role '{value}'. Allowed roles for this organization: {org.allowed_roles}"
                )
        return value
