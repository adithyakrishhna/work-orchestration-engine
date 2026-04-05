from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only the admin role can access"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsManagerOrAbove(BasePermission):
    """
    Admin and the second-highest role (index 1 in allowed_roles) can access.
    Default: admin and manager.
    For dynamic orgs, the first two roles in allowed_roles are considered 'above'.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if request.user.role == 'admin':
            return True
        org = request.user.organization
        if org and org.allowed_roles:
            # First two roles are considered management-level
            management_roles = org.allowed_roles[:2]
            return request.user.role in management_roles
        # Fallback
        return request.user.role in ('admin', 'manager')


class IsSameOrganization(BasePermission):
    """Users can only access data from their own organization"""
    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'organization'):
            return obj.organization == request.user.organization
        if hasattr(obj, 'role'):
            return obj.organization == request.user.organization
        return False


class TaskPermission(BasePermission):
    """
    - Anyone in the org can view tasks
    - Management roles (top 2) can update any task
    - Other roles can update their own tasks
    - Only admin can delete
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if view.action in ('list', 'retrieve', 'create'):
            return True
        if view.action in ('update', 'partial_update'):
            return True  # Object-level check below
        if view.action == 'destroy':
            return request.user.role == 'admin'
        return True

    def has_object_permission(self, request, view, obj):
        if obj.organization != request.user.organization:
            return False
        if request.user.role == 'admin':
            return True
        org = request.user.organization
        management_roles = org.allowed_roles[:2] if (org and org.allowed_roles) else ['admin', 'manager']
        if request.user.role in management_roles and view.action in ('update', 'partial_update'):
            return True
        if view.action in ('update', 'partial_update'):
            return obj.assigned_to == request.user or obj.created_by == request.user
        return True

class IsNotViewer(BasePermission):
    """
    Block the last role in the org (viewer/read-only) from write operations.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if view.action in ('list', 'retrieve'):
            return True
        if view.action == 'create':
            # Block viewer (last role) from creating
            org = request.user.organization
            if org and org.allowed_roles:
                return request.user.role != org.allowed_roles[-1]
            return request.user.role != 'viewer'
        if view.action in ('update', 'partial_update'):
            return True  # Object-level check below
        if view.action == 'destroy':
            return request.user.role == 'admin' or (
                org and org.allowed_roles and request.user.role == org.allowed_roles[0]
            )
        return True