from celery import shared_task
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils.html import strip_tags

from posts.models import Post


@shared_task
def send_email_notification(subject, post_id, recipient_list):
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


def build_absolute_url(relative_url):
    return settings.SITE_DOMAIN + relative_url


class EmailNotification:
    def __init__(self, subject, post, recipient_list):
        self.subject = subject
        self.post = post
        self.recipient_list = recipient_list
        self.post_url = build_absolute_url(reverse('post_detail', args=[post.id]))
        self.unsubscribe_url = build_absolute_url(reverse('delete_email_subscriber'))

    def send(self):
        html_content = render_to_string(
            'email/post_notification.html',
            {'post': self.post, 'post_url': self.post_url, 'unsubscribe_url': self.unsubscribe_url}
        )
        # Create a text version for email clients that don't support HTML
        text_content = strip_tags(html_content)
        email = EmailMultiAlternatives(self.subject, text_content, settings.EMAIL_HOST_USER, self.recipient_list)
        email.attach_alternative(html_content, 'text/html')
        email.send()
