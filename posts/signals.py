import logging

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from utils.utils import EmailNotification, send_email_notification

from .models import Post, Category, ViewedPost
from users.models import EmailSubscriber

logger = logging.getLogger(__name__.split('.')[0])


@receiver(pre_save, sender=Post)
@receiver(pre_save, sender=Category)
@receiver(pre_save, sender=ViewedPost)
def track_changes(sender, instance, **kwargs):
    if instance.pk:
        initial = SimpleLazyObject(lambda: sender.objects.get(pk=instance.pk))
        action = 'Updated'
    else:
        initial = SimpleLazyObject(lambda: sender())
        action = 'Created'

    changed_fields = []
    for field in sender._meta.fields:
        field_name = field.name
        initial_value = getattr(initial, field_name, None)
        current_value = getattr(instance, field_name, None)
        if action == 'Created' or initial_value != current_value:
            changed_fields.append((field_name, initial_value, current_value))

    if changed_fields:
        change_desc = ', '.join([f'{field}: {init} -> {curr}' for field, init, curr in changed_fields])
        logger.warning(f'{action} {sender.__name__} {instance.pk if instance.pk else ""}: {change_desc}')


@receiver(pre_save, sender=Post)
def set_date(sender, instance, **kwargs):
    logger.info(f'Starting set_date for post {instance.pk}')
    initial = SimpleLazyObject(lambda: sender.objects.get(pk=instance.pk))
    if not initial.is_published and instance.is_published:
        date_to_set = instance.date_scheduled if instance.date_scheduled else timezone.now()
        sender.objects.filter(pk=instance.pk).update(date_published=date_to_set)
        logger.info(f'date_published set to {date_to_set} for new post {instance.pk}')


@receiver(pre_save, sender=Post)
def post_create_notification(sender, instance, **kwargs):
    logger.info(f'Starting post_create_notification for post {instance.pk}')
    initial = SimpleLazyObject(lambda: sender.objects.get(pk=instance.pk))
    if not initial.is_published and instance.is_published:
        subject = f"New post on DataSamurai`s blog: {instance.title}"
        recipient_list = [subscriber.user.email for subscriber in EmailSubscriber.objects.all()]

        email_notification = EmailNotification(subject, instance, recipient_list)
        email_notification.send()

        # Enqueueing Celery task
        # send_email_notification(subject, instance.pk, recipient_list)

        logger.info(f'Email post notification sent to {recipient_list}')
