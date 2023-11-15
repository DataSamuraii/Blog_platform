import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

logger = logging.getLogger(__name__.split('.')[0])


class CustomUser(AbstractUser):
    is_banned = models.BooleanField(default=False)

    def delete(self, *args, **kwargs):
        logger.warning(f"Deleting user: {self.username} (ID: {self.pk})")
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.username

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

    def delete(self, *args, **kwargs):
        logger.warning(f"Deleting UnbanRequest: {self.id} for user {self.user.username}")
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"Unban Request by {self.user.username}"

    class Meta:
        ordering = ['id']
