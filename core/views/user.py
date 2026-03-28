from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from core.models import User
from core.serializers import UserSerializer, UserCreateSerializer
from core.permissions import IsAdmin, IsManagerOrAbove


class UserViewSet(viewsets.ModelViewSet):
    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        return UserSerializer

    def get_queryset(self):
        return User.objects.filter(organization=self.request.user.organization)

    def get_permissions(self):
        if self.action == 'create':
            return [IsManagerOrAbove()]
        if self.action == 'destroy':
            return [IsAdmin()]
        return super().get_permissions()

    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user's profile"""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)