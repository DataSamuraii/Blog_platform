from celery import shared_task
from django.utils import timezone
from .models import Post
import logging

logger = logging.getLogger(__name__.split('.')[0])


@shared_task
def publish_scheduled_posts():
    logger.info('Starting publish_scheduled_posts celery task')
    try:
        posts_to_publish = Post.objects.filter(date_scheduled__lte=timezone.now(), is_published=False)
        for post in posts_to_publish:
            post.is_published = True
            post.save()
            logger.info(f'publish_scheduled_posts set is_published to {post.is_published} for post {post.pk}')
    except Exception as e:
        logger.error(f'Error publishing scheduled posts: {e}')
