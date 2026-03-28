from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    OrganizationViewSet, UserViewSet, TeamViewSet,
    WorkflowConfigViewSet, TransitionRuleViewSet,
    TaskViewSet, CommentViewSet, AuditLogViewSet,
    DashboardOverviewView, TeamPerformanceView,
    RecentActivityView, SLACheckView,
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
    # Dashboard endpoints
    path('dashboard/overview/', DashboardOverviewView.as_view(), name='dashboard-overview'),
    path('dashboard/team-performance/', TeamPerformanceView.as_view(), name='team-performance'),
    path('dashboard/activity/', RecentActivityView.as_view(), name='recent-activity'),
    path('dashboard/sla-check/', SLACheckView.as_view(), name='sla-check'),
]