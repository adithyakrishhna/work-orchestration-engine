from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet, UserViewSet, TeamViewSet,
    WorkflowConfigViewSet, TransitionRuleViewSet,
    TaskViewSet, CommentViewSet, AuditLogViewSet,
)

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'users', UserViewSet, basename='user')
router.register(r'teams', TeamViewSet, basename='team')
router.register(r'workflows', WorkflowConfigViewSet, basename='workflow')
router.register(r'transitions', TransitionRuleViewSet, basename='transition')
router.register(r'tasks', TaskViewSet, basename='task')
router.register(r'comments', CommentViewSet, basename='comment')
router.register(r'audit-logs', AuditLogViewSet, basename='audit-log')

urlpatterns = [
    path('', include(router.urls)),
]