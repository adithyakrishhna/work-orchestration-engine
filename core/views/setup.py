from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from core.models import Organization, User, WorkflowConfig, TransitionRule, Team


class OrganizationSetupView(APIView):
    """
    POST /api/v1/setup/
    One-stop setup endpoint for new organizations.
    Creates org, admin user, default workflow, and optional team — all in one call.
    No authentication required (this is for first-time setup).
    """
    permission_classes = [AllowAny]

    def post(self, request):
        data = request.data

        # Validate required fields
        required = ['org_name', 'org_slug', 'admin_username', 'admin_password']
        missing = [f for f in required if not data.get(f)]
        if missing:
            return Response(
                {'error': f'Missing required fields: {missing}'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Check if slug already exists
        if Organization.objects.filter(slug=data['org_slug']).exists():
            return Response(
                {'error': f"Organization with slug '{data['org_slug']}' already exists."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 1. Create Organization with custom config
        org = Organization.objects.create(
            name=data['org_name'],
            slug=data['org_slug'],
            allowed_roles=data.get('roles', ['admin', 'manager', 'engineer', 'viewer']),
            allowed_priorities=data.get('priorities', ['critical', 'high', 'medium', 'low']),
            allowed_task_types=data.get('task_types', ['bug', 'feature', 'task', 'improvement']),
        )

        # 2. Create Admin User
        admin_user = User.objects.create_user(
            username=data['admin_username'],
            password=data['admin_password'],
            email=data.get('admin_email', ''),
            role='admin',
            organization=org,
        )

        # 3. Create Default Workflow
        states = data.get('workflow_states', ['open', 'in_progress', 'review', 'testing', 'done', 'cancelled'])
        initial = data.get('initial_state', states[0])
        finals = data.get('final_states', [states[-2], states[-1]] if len(states) >= 2 else [states[-1]])

        workflow = WorkflowConfig.objects.create(
            name=data.get('workflow_name', f'{org.name} Default Workflow'),
            organization=org,
            is_default=True,
            allowed_states=states,
            initial_state=initial,
            final_states=finals,
        )

        # 4. Create default transitions (sequential flow)
        roles = org.allowed_roles
        management_roles = roles[:2] if len(roles) >= 2 else roles
        all_non_viewer = [r for r in roles if r != roles[-1]] if len(roles) > 1 else roles

        # Create sequential transitions
        active_states = [s for s in states if s not in finals]
        for i in range(len(active_states) - 1):
            TransitionRule.objects.create(
                workflow=workflow,
                from_state=active_states[i],
                to_state=active_states[i + 1],
                allowed_roles=all_non_viewer,
            )
            # Allow management to revert
            if i > 0:
                TransitionRule.objects.create(
                    workflow=workflow,
                    from_state=active_states[i],
                    to_state=active_states[i - 1],
                    allowed_roles=management_roles,
                )

        # Last active state to first final state
        if active_states and finals:
            TransitionRule.objects.create(
                workflow=workflow,
                from_state=active_states[-1],
                to_state=finals[0],
                allowed_roles=management_roles,
            )

        # Allow cancellation from any active state
        cancel_state = finals[-1] if len(finals) > 1 else None
        if cancel_state:
            for s in active_states:
                TransitionRule.objects.get_or_create(
                    workflow=workflow,
                    from_state=s,
                    to_state=cancel_state,
                    defaults={'allowed_roles': management_roles},
                )

        # Reopen from done (admin only)
        if finals and active_states:
            TransitionRule.objects.create(
                workflow=workflow,
                from_state=finals[0],
                to_state=active_states[0],
                allowed_roles=['admin'],
            )

        # 5. Create optional team
        team = None
        if data.get('team_name'):
            team = Team.objects.create(
                name=data['team_name'],
                organization=org,
                lead=admin_user,
            )

        # 6. Generate tokens for the admin
        refresh = RefreshToken.for_user(admin_user)

        return Response({
            'message': f"Organization '{org.name}' created successfully!",
            'organization': {
                'id': str(org.id),
                'name': org.name,
                'slug': org.slug,
                'allowed_roles': org.allowed_roles,
                'allowed_priorities': org.allowed_priorities,
                'allowed_task_types': org.allowed_task_types,
            },
            'admin_user': {
                'id': str(admin_user.id),
                'username': admin_user.username,
                'role': admin_user.role,
            },
            'workflow': {
                'id': str(workflow.id),
                'name': workflow.name,
                'states': workflow.allowed_states,
                'initial_state': workflow.initial_state,
                'final_states': workflow.final_states,
                'transitions_created': workflow.transitions.count(),
            },
            'team': {
                'id': str(team.id),
                'name': team.name,
            } if team else None,
            'tokens': {
                'access': str(refresh.access_token),
                'refresh': str(refresh),
            },
        }, status=status.HTTP_201_CREATED) 