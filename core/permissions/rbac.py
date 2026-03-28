from rest_framework.permissions import BasePermission


class IsAdmin(BasePermission):
    """Only admins can access"""
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'admin'


class IsManagerOrAbove(BasePermission):
    """Admins and managers can access"""
    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.role in ('admin', 'manager')
        )


class IsSameOrganization(BasePermission):
    """Users can only access data from their own organization"""
    def has_object_permission(self, request, view, obj):
        # Handle objects that have org directly
        if hasattr(obj, 'organization'):
            return obj.organization == request.user.organization
        # Handle User objects
        if hasattr(obj, 'role'):
            return obj.organization == request.user.organization
        return False


class TaskPermission(BasePermission):
    """
    - Anyone in the org can view tasks
    - Engineers can create and update their own tasks
    - Managers can update any task in their org
    - Admins can do everything
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        if view.action in ('list', 'retrieve', 'create'):
            return True
        if view.action in ('update', 'partial_update'):
            return request.user.role in ('admin', 'manager', 'engineer')
        if view.action == 'destroy':
            return request.user.role == 'admin'
        return True

    def has_object_permission(self, request, view, obj):
        # Must be same org
        if obj.organization != request.user.organization:
            return False
        # Admins can do anything
        if request.user.role == 'admin':
            return True
        # Managers can update any task in org
        if request.user.role == 'manager' and view.action in ('update', 'partial_update'):
            return True
        # Engineers can only update tasks assigned to them or created by them
        if request.user.role == 'engineer' and view.action in ('update', 'partial_update'):
            return obj.assigned_to == request.user or obj.created_by == request.user
        return True