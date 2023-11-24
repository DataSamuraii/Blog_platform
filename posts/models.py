import logging

import bleach
from ckeditor.fields import RichTextField
from django.conf import settings
from django.db import models

logger = logging.getLogger(__name__.split('.')[0])


class Post(models.Model):
    title = models.CharField(max_length=100, unique=True)
    content = RichTextField()
    category = models.ForeignKey('Category', on_delete=models.SET_NULL, null=True)
    date_scheduled = models.DateTimeField(null=True, blank=True)
    date_published = models.DateTimeField(null=True, blank=True)
    views = models.PositiveIntegerField(default=0)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    is_published = models.BooleanField(default=False)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Clean the content field with bleach using the settings from settings.py
        self.content = bleach.clean(
            self.content,
            tags=settings.ALLOWED_TAGS,
            attributes=settings.ALLOWED_ATTRIBUTES,
            protocols=settings.ALLOWED_PROTOCOLS,
            strip=settings.STRIP,
            strip_comments=settings.STRIP_COMMENTS,
        )
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        logger.warning(f"Deleting post: {self.title} (ID: {self.pk})")
        super().delete(*args, **kwargs)

    class Meta:
        ordering = ['-date_published']


class Category(models.Model):
    title = models.CharField(max_length=30)
    description = models.TextField()

    def delete(self, *args, **kwargs):
        logger.warning(f"Deleting category: {self.title} (ID: {self.pk})")
        super().delete(*args, **kwargs)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['title']
        verbose_name_plural = 'Categories'


class ViewedPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        logger.warning(f"Deleting ViewedPost ID: {self.pk}")
        super().delete(*args, **kwargs)


class Comment(models.Model):
    content = models.CharField(max_length=500)
    author = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    post = models.ForeignKey('Post', on_delete=models.CASCADE)
    timestamp = models.DateTimeField(auto_now_add=True)
    parent_comment = models.ForeignKey('self', on_delete=models.CASCADE, null=True, default=None)
    is_deleted = models.BooleanField(default=False)
    is_profane = models.BooleanField(default=False)
    is_negative = models.BooleanField(default=False)

    @property
    def likes_count(self):
        return self.reactions.filter(reaction_type='like').count()

    @property
    def dislikes_count(self):
        return self.reactions.filter(reaction_type='dislike').count()

    def delete(self, *args, **kwargs):
        logger.warning(f"Deleting comment: {self.content} (ID: {self.pk})")
        super().delete(*args, **kwargs)

    def __str__(self):
        return str(self.id)

    class Meta:
        ordering = ['timestamp']


class CommentReaction(models.Model):
    REACTION_CHOICES = [
        ('like', 'Like'),
        ('dislike', 'Dislike')
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='reactions', on_delete=models.CASCADE)
    reaction_type = models.CharField(max_length=10, choices=REACTION_CHOICES)

    class Meta:
        unique_together = ['user', 'comment']
