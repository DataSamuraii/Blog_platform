from django.db import models
from django.conf import settings


class Post(models.Model):
    title = models.CharField(max_length=50, unique=True)
    content = models.TextField()
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    date_published = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(auto_now=True)
    views = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-date_published']


class Category(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']


class ViewedPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
