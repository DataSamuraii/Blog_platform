import logging

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils import timezone
from django.utils.functional import SimpleLazyObject
from utils.utils import EmailNotification

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


@receiver(post_save, sender=Post)
def set_date(sender, instance, created, **kwargs):
    if created and instance.is_published:
        logger.info(f'Starting set_date for post {instance.pk}')
        date_to_set = instance.date_scheduled if instance.date_scheduled else timezone.now()
        sender.objects.filter(pk=instance.pk).update(date_published=date_to_set)
        logger.info(f'date_published set to {date_to_set} for new post {instance.pk}')


@receiver(post_save, sender=Post)
def post_create_notification(sender, instance, created, **kwargs):
    if created:
        logger.info(f'Starting post_create_notification for post {instance.pk}')
        subject = f"New post on DataSamurai`s blog: {instance.title}"
        post = instance
        recipient_list = [subscriber.user.email for subscriber in EmailSubscriber.objects.all()]

        email_notification = EmailNotification(subject, post, recipient_list)
        email_notification.send()
        logger.info(f'Notification sent to {recipient_list}')
