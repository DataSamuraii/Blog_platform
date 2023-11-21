from __future__ import absolute_import, unicode_literals

import os

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Blog_platform.settings')

app = Celery('Blog_platform')
app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

# To start celery, run:
# celery -A Blog_platform beat -l info
# celery -A Blog_platform worker -l info -P solo
