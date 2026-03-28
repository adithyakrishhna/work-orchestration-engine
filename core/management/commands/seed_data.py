from django.core.management.base import BaseCommand
from core.models import Organization, User, Team, WorkflowConfig, TransitionRule


class Command(BaseCommand):
    help = 'Seed database with sample workflow data'

    def handle(self, *args, **kwargs):
        # Create Organization
        org, _ = Organization.objects.get_or_create(
            slug='acme',
            defaults={'name': 'Acme Corporation'}
        )
        self.stdout.write(f"Organization: {org.name}")

        # Create Users
        admin = self._create_user('admin_user', 'admin', org)
        manager = self._create_user('manager_user', 'manager', org)
        dev1 = self._create_user('dev_alice', 'engineer', org, skills=['python', 'django', 'aws'])
        dev2 = self._create_user('dev_bob', 'engineer', org, skills=['javascript', 'react', 'node'])
        viewer = self._create_user('viewer_user', 'viewer', org)

        # Create Team
        team, _ = Team.objects.get_or_create(
            name='Backend Team',
            organization=org,
            defaults={'lead': manager}
        )
        team.members.add(dev1, dev2)
        self.stdout.write(f"Team: {team.name}")

        # Create Workflow — this is the state machine definition
        workflow, _ = WorkflowConfig.objects.get_or_create(
            name='Standard Bug Tracking',
            organization=org,
            defaults={
                'is_default': True,
                'allowed_states': ['open', 'in_progress', 'review', 'testing', 'done', 'cancelled'],
                'initial_state': 'open',
                'final_states': ['done', 'cancelled'],
            }
        )
        self.stdout.write(f"Workflow: {workflow.name}")

        # Define Transition Rules — WHO can move WHAT to WHERE
        transitions = [
            # From 'open'
            ('open', 'in_progress', ['admin', 'manager', 'engineer']),
            ('open', 'cancelled', ['admin', 'manager']),
            # From 'in_progress'
            ('in_progress', 'review', ['admin', 'manager', 'engineer']),
            ('in_progress', 'open', ['admin', 'manager']),
            ('in_progress', 'cancelled', ['admin', 'manager']),
            # From 'review'
            ('review', 'testing', ['admin', 'manager']),
            ('review', 'in_progress', ['admin', 'manager']),
            # From 'testing'
            ('testing', 'done', ['admin', 'manager']),
            ('testing', 'in_progress', ['admin', 'manager', 'engineer']),
            # From 'done' — only admin can reopen
            ('done', 'open', ['admin']),
        ]

        for from_s, to_s, roles in transitions:
            TransitionRule.objects.get_or_create(
                workflow=workflow,
                from_state=from_s,
                to_state=to_s,
                defaults={'allowed_roles': roles}
            )

        self.stdout.write(self.style.SUCCESS(
            '\nSeed data created successfully!'
            '\n\nUsers created (password for all: testpass123):'
            '\n  admin_user (admin)'
            '\n  manager_user (manager)'
            '\n  dev_alice (engineer) — skills: python, django, aws'
            '\n  dev_bob (engineer) — skills: javascript, react, node'
            '\n  viewer_user (viewer)'
            '\n\nWorkflow: Standard Bug Tracking'
            '\n  States: open → in_progress → review → testing → done'
            '\n  Final states: done, cancelled'
        ))

    def _create_user(self, username, role, org, skills=None):
        user, created = User.objects.get_or_create(
            username=username,
            defaults={
                'role': role,
                'organization': org,
                'skills': skills or [],
            }
        )
        if created:
            user.set_password('testpass123')
            user.save()
        self.stdout.write(f"User: {username} ({role})")
        return user