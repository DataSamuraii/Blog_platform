from datetime import timedelta
from django.core.management.base import BaseCommand
from django.utils import timezone
from analytics.models import ViewedPost


# To run the command: python manage.py purge_old_views or use button in admin
class Command(BaseCommand):
    help = 'Purge old viewed post records'

    def handle(self, *args, **options):
        time_threshold = timezone.now() - timedelta(hours=24)  # 24 hours old records
        old_records = ViewedPost.objects.filter(timestamp__lte=time_threshold)
        count = old_records.count()
        old_records.delete()

        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} old records'))
