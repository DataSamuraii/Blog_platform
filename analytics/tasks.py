from celery import shared_task

from .models import VisitorPageData


@shared_task
def log_page_visit(user_id, ip_address, page):
    VisitorPageData.objects.create(user=user_id, ip_address=ip_address, page=page)
