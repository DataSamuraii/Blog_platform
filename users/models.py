import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

logger = logging.getLogger(__name__.split('.')[0])


class CustomUser(AbstractUser):
    is_banned = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if self.pk is not None:
            initial = type(self).objects.get(pk=self.pk)
            if initial.is_banned != self.is_banned:
                logger.warning(
                    f"User {self.username}'s 'is_banned' changed from {initial.is_banned} to {self.is_banned}"
                )

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        logger.warning(f"Deleting user: {self.username} (ID: {self.pk})")
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['id']


class UnbanRequest(models.Model):
    UNBAN_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('reviewed', 'Reviewed'),
        ('approved', 'Approved'),
        ('denied', 'Denied'),
    ]
    user = models.ForeignKey(get_user_model(), on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=UNBAN_STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        if self.pk is not None:
            initial = type(self).objects.get(pk=self.pk)
            if initial.status != self.status:
                logger.warning(
                    f"UnbanRequest {self.id} 'status' changed from {initial.status} to {self.status}"
                )

        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        logger.warning(f"Deleting UnbanRequest: {self.id} for user {self.user.username}")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Unban Request by {self.user.username} - Status: {self.get_status_display()}"

    class Meta:
        ordering = ['id']
