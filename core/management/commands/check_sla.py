from django.core.management.base import BaseCommand
from core.services import SLAService


class Command(BaseCommand):
    help = 'Check all active tasks for SLA breaches'

    def handle(self, *args, **kwargs):
        results = SLAService.check_all_sla()
        self.stdout.write(
            self.style.SUCCESS(
                f"SLA check complete: {results['checked']} checked, "
                f"{results['breached']} newly breached"
            )
        )