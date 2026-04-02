from rest_framework import viewsets
from core.models import Team
from core.serializers import TeamSerializer
from core.permissions import IsManagerOrAbove


class TeamViewSet(viewsets.ModelViewSet):
    serializer_class = TeamSerializer

    def get_queryset(self):
        return Team.objects.filter(organization=self.request.user.organization)

    def get_permissions(self):
        if self.action in ('create', 'update', 'partial_update', 'destroy'):
            return [IsManagerOrAbove()]
        return super().get_permissions()
    
    def perform_create(self, serializer):
        serializer.save(organization=self.request.user.organization)