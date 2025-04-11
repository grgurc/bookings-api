from django.core.management.base import BaseCommand
from bookings.tasks import sync_all_bookings


class Command(BaseCommand):
    help = 'Performs initial sync of all bookings from the external API'

    def handle(self, *args, **options):
        self.stdout.write('Starting initial sync of all bookings...')
        sync_all_bookings(is_sync=True)
        self.stdout.write(self.style.SUCCESS('Initial sync completed successfully')) 