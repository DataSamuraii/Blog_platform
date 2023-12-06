import logging

from django.contrib.auth import get_user_model
from django.db import models

from posts.models import Post

logger = logging.getLogger(__name__.split('.')[0])


class ViewedPost(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        logger.warning(f"Deleting ViewedPost ID: {self.pk}")
        super().delete(*args, **kwargs)


class VisitorGeoData(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(unpack_ipv4=True)
    country = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def delete(self, *args, **kwargs):
        logger.warning(f'Deleting VisitorGeoData: {self.user} {self.ip_address} (ID: {self.pk})')
        super().delete(*args, **kwargs)

    def __str__(self):
        return f'VisitorGeoData: {self.user}, {self.ip_address} - {self.country}, {self.city}'

    class Meta:
        ordering = ['id']


class VisitorPageData(models.Model):
    user = models.ForeignKey(get_user_model(), on_delete=models.SET_NULL, null=True, blank=True)
    ip_address = models.GenericIPAddressField(unpack_ipv4=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    page = models.URLField()

    def delete(self, *args, **kwargs):
        logger.warning(f'Deleting VisitorPageData: {self.user} {self.ip_address} (ID: {self.pk})')
        super().delete(*args, **kwargs)

    def __str__(self):
        return f'VisitorPageData: {self.user} visited {self.page} at {self.timestamp}'

    class Meta:
        ordering = ['id']


class UserInteraction(models.Model):
    interaction_type = models.CharField(max_length=30)
    x_coordinate = models.IntegerField()
    y_coordinate = models.IntegerField()
    page = models.URLField()

    def delete(self, *args, **kwargs):
        logger.warning(
            f'Deleting UserInteraction: {self.interaction_type} {self.x_coordinate, self.y_coordinate} (ID: {self.pk})'
        )
        super().delete(*args, **kwargs)

    def __str__(self):
        return f"{self.interaction_type} at ({self.x_coordinate}, {self.y_coordinate})"

    class Meta:
        ordering = ['id']
