import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags
from flair.data import Sentence
from flair.models import TextClassifier
from profanity_check import predict_prob

from utils.utils import build_absolute_url
from .models import Post, Comment

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


@shared_task
def send_email_post_notification(subject, post_id, recipient_list):
    post = Post.objects.get(pk=post_id)
    post_url = build_absolute_url(reverse('post_detail', args=[post.id]))
    unsubscribe_url = build_absolute_url(reverse('delete_email_subscriber'))

    html_content = render_to_string(
        'email/post_notification.html',
        {'post': post, 'post_url': post_url, 'unsubscribe_url': unsubscribe_url}
    )
    text_content = strip_tags(html_content)

    email = EmailMultiAlternatives(subject, text_content, settings.EMAIL_HOST_USER, recipient_list)
    email.attach_alternative(html_content, 'text/html')
    email.send()


@shared_task
def check_comment_profanity(comment_id):
    logger.info(f'Starting check_comment_profanity celery task for comment {comment_id}')
    comment = Comment.objects.get(id=comment_id)
    probability = predict_prob([comment.content])[0]

    if probability > 0.5:
        comment.is_profane = True
        comment.save()
        logger.info(f'Comment {comment_id} marked profane')


@shared_task
def check_comment_negativity(comment_id):
    logger.info(f'Starting check_comment_negativity celery task for comment {comment_id}')
    comment = Comment.objects.get(id=comment_id)
    sentence = Sentence(comment.content)
    classifier = TextClassifier.load('en-sentiment')
    classifier.predict(sentence)
    sentiment = sentence.labels[0].to_dict()
    comment.is_negative = (sentiment['value'] == 'NEGATIVE')
    comment.save()
    logger.info(f'Comment {comment_id} is_negative marked {comment.is_negative}')
