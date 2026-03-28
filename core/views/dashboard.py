from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from core.services import SLAService, DashboardService


class DashboardOverviewView(APIView):
    """
    GET /api/v1/dashboard/overview/
    Returns high-level task statistics for the organization.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.user.organization
        overview = DashboardService.get_overview(org)
        sla = SLAService.get_sla_summary(org)
        return Response({
            'overview': overview,
            'sla': sla,
        })


class TeamPerformanceView(APIView):
    """
    GET /api/v1/dashboard/team-performance/
    Returns per-user performance metrics.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.user.organization
        performance = DashboardService.get_team_performance(org)
        return Response({'team_performance': performance})


class RecentActivityView(APIView):
    """
    GET /api/v1/dashboard/activity/
    Returns recent activity feed.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.user.organization
        limit = int(request.query_params.get('limit', 20))
        activity = DashboardService.get_recent_activity(org, limit=limit)
        return Response({'recent_activity': activity})


class SLACheckView(APIView):
    """
    POST /api/v1/dashboard/sla-check/
    Triggers SLA breach detection across all active tasks.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        results = SLAService.check_all_sla()
        return Response({
            'message': 'SLA check completed',
            'results': results,
        })