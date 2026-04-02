from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from core.models import Task, AuditLog
from .priority_scorer import AIPriorityScorer
from .task_router import AITaskRouter
from .nl_query import NLQueryEngine
from rest_framework import status

class AIPriorityScoringView(APIView):
    """
    POST /api/v1/ai/score-priority/
    Body: {"task_id": "uuid"}
    Scores a task and saves the AI priority score.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        task_id = request.data.get('task_id')
        if not task_id:
            return Response(
                {'error': 'task_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            task = Task.objects.get(
                id=task_id,
                organization=request.user.organization,
            )
        except Task.DoesNotExist:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Score the task
        result = AIPriorityScorer.score(task)
        estimated_hours = AIPriorityScorer.estimate_hours(task)

        # Save to task
        task.ai_priority_score = result['score']
        task.ai_estimated_hours = estimated_hours
        task.save()

        return Response({
            'task_key': task.task_key,
            'title': task.title,
            'priority_analysis': result,
            'estimated_hours': estimated_hours,
        })


class AIBulkScoringView(APIView):
    """
    POST /api/v1/ai/score-all/
    Score all active tasks in the organization.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        from core.models import WorkflowConfig
        final_states = set()
        for wf in WorkflowConfig.objects.filter(organization=request.user.organization):
            final_states.update(wf.final_states or [])
        if not final_states:
            final_states = {'done', 'cancelled'}
        tasks = Task.objects.filter(
            organization=request.user.organization,
        ).exclude(current_state__in=list(final_states))

        results = []
        for task in tasks:
            score_data = AIPriorityScorer.score(task)
            hours = AIPriorityScorer.estimate_hours(task)
            task.ai_priority_score = score_data['score']
            task.ai_estimated_hours = hours
            task.save()
            results.append({
                'task_key': task.task_key,
                'score': score_data['score'],
                'estimated_hours': hours,
                'explanation': score_data['explanation'],
            })

        results.sort(key=lambda x: x['score'], reverse=True)
        return Response({
            'scored_count': len(results),
            'results': results,
        })


class AITaskRoutingView(APIView):
    """
    POST /api/v1/ai/recommend-assignee/
    Body: {"task_id": "uuid"}
    Returns ranked list of recommended assignees.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        task_id = request.data.get('task_id')
        if not task_id:
            return Response(
                {'error': 'task_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            task = Task.objects.get(
                id=task_id,
                organization=request.user.organization,
            )
        except Task.DoesNotExist:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        result = AITaskRouter.recommend(task)
        return Response(result)


class AIAutoAssignView(APIView):
    """
    POST /api/v1/ai/auto-assign/
    Body: {"task_id": "uuid"}
    Automatically assigns the task to the best candidate.
    Only admins and managers can auto-assign.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Permission check — only admins and managers can assign
        org = request.user.organization
        management_roles = org.allowed_roles[:2] if (org and org.allowed_roles and len(org.allowed_roles) >= 2) else ['admin', 'manager']
        if request.user.role not in management_roles:
            return Response(
                {'error': 'Only admins and managers can auto-assign tasks.'},
                status=status.HTTP_403_FORBIDDEN,
            )

        task_id = request.data.get('task_id')
        if not task_id:
            return Response(
                {'error': 'task_id is required'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            task = Task.objects.get(
                id=task_id,
                organization=request.user.organization,
            )
        except Task.DoesNotExist:
            return Response(
                {'error': 'Task not found'},
                status=status.HTTP_404_NOT_FOUND,
            )

        best_user = AITaskRouter.auto_assign(task)
        if not best_user:
            return Response({
                'message': 'No suitable candidate found',
                'task_key': task.task_key,
            })

        # Assign using state machine service
        from core.services import StateMachineService
        task = StateMachineService.assign_task(
            task, best_user, request.user,
            reason=f'AI auto-assigned based on skill match and availability'
        )

        recommendation = AITaskRouter.recommend(task)
        return Response({
            'message': f'Task auto-assigned to {best_user.username}',
            'task_key': task.task_key,
            'assigned_to': best_user.username,
            'recommendation_details': recommendation,
        })

class NLQueryView(APIView):
    """
    POST /api/v1/ai/query/
    Body: {"question": "show me all critical bugs assigned to alice"}
    Natural language task search.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        question = request.data.get('question', '').strip()
        if not question:
            return Response(
                {'error': 'question is required. Try: "show me all critical bugs" or "unassigned high priority tasks"'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        result = NLQueryEngine.query(question, request.user.organization)

        # Handle "my tasks" flag — needs request context
        if result['parsed_filters'].get('my_tasks'):
            from core.models import WorkflowConfig
            final_states = set()
            for wf in WorkflowConfig.objects.filter(organization=request.user.organization):
                final_states.update(wf.final_states or [])
            if not final_states:
                final_states = {'done', 'cancelled'}
            my_tasks = Task.objects.filter(
                organization=request.user.organization,
                assigned_to=request.user,
            ).exclude(current_state__in=list(final_states))

            result['results'] = [
                {
                    'task_key': t.task_key,
                    'title': t.title,
                    'state': t.current_state,
                    'priority': t.priority,
                    'type': t.task_type,
                    'assigned_to': t.assigned_to.username if t.assigned_to else None,
                    'sla_breached': t.sla_breached,
                    'created_at': t.created_at.isoformat(),
                }
                for t in my_tasks[:50]
            ]
            result['count'] = len(result['results'])
            result['explanation'] = f"Found {result['count']} active tasks assigned to you"

        return Response(result)