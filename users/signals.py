import logging

from django.db.models.signals import pre_save, post_save
from django.dispatch import receiver
from django.utils.functional import SimpleLazyObject

from utils.utils import EmailUserNotification
from .models import CustomUser, UnbanRequest, EmailSubscriber

logger = logging.getLogger(__name__.split('.')[0])


@receiver(pre_save, sender=CustomUser)
@receiver(pre_save, sender=UnbanRequest)
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


@receiver(post_save, sender=CustomUser)
def create_subscriber_for_new_user(sender, instance, created, **kwargs):
    logger.info(f'Starting create_subscriber_for_new_user for new user {instance.pk}')
    if created:
        EmailSubscriber.objects.create(user=instance)
        logger.info(f'Created new email subscription for new user {instance.pk}')


@receiver(post_save, sender=CustomUser)
def user_edit_notification(sender, instance, created, **kwargs):
    logger.info(f'Starting user_edit_notification for user {instance.pk}')
    subject = f'Your account data has been changed at DataSamurai`s blog'
    recipient_email = instance.email

    email_notification = EmailUserNotification(subject, instance, recipient_email)
    email_notification.send()

    logger.info(f'Email user notification sent to {recipient_email}')
