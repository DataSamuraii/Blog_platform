import logging
import os

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AbstractUser
from django.db import models

logger = logging.getLogger(__name__.split('.')[0])


class CustomUser(AbstractUser):
    is_banned = models.BooleanField(default=False)
    bio = models.CharField(max_length=200, blank=True, null=True, default=None)
    social_media = models.JSONField(default=dict, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', blank=True, null=True)

    def delete_old_profile_picture(self, new_file):
        old_file = CustomUser.objects.get(pk=self.pk).profile_picture
        if old_file and old_file != new_file and os.path.isfile(old_file.path):
            os.remove(old_file.path)

    def save(self, *args, **kwargs):
        if self.profile_picture:
            self.delete_old_profile_picture(self.profile_picture)
        super(CustomUser, self).save(*args, **kwargs)

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
