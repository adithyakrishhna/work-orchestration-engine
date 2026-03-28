from rest_framework import viewsets
from core.models import Organization
from core.serializers import OrganizationSerializer
from core.permissions import IsAdmin


class OrganizationViewSet(viewsets.ModelViewSet):
    serializer_class = OrganizationSerializer

    def get_queryset(self):
        # Users only see their own organization
        if self.request.user.is_superuser:
            return Organization.objects.all()
        return Organization.objects.filter(id=self.request.user.organization_id)

    def get_permissions(self):
        if self.action in ('create', 'destroy'):
            return [IsAdmin()]
        return super().get_permissions()