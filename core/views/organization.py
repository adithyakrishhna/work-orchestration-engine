from rest_framework import viewsets
from core.models import Organization
from core.serializers import OrganizationSerializer
from core.permissions import IsAdmin


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        # Superusers and admins see all organizations
        if self.request.user.is_superuser or self.request.user.role == 'admin':
            return Organization.objects.all()
        # Others see only their own
        return Organization.objects.filter(id=self.request.user.organization_id)

    def get_permissions(self):
        if self.action in ('create', 'destroy'):
            return [IsAdmin()]
        return super().get_permissions()