import logging

from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils.functional import SimpleLazyObject

from .models import ViewedPost, VisitorGeoData, VisitorPageData

logger = logging.getLogger(__name__.split('.')[0])


@receiver(pre_save, sender=ViewedPost)
@receiver(pre_save, sender=VisitorGeoData)
@receiver(pre_save, sender=VisitorPageData)
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
        logger.info(f'{action} {sender.__name__} {instance.pk if instance.pk else ""}: {change_desc}')
