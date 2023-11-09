from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model


class CustomUser(AbstractUser):
    is_banned = models.BooleanField(default=False)


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

    def __str__(self):
        return f"Unban Request by {self.user.username} - Status: {self.get_status_display()}"
