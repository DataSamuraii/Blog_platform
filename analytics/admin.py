import logging
from datetime import timedelta

from django.contrib import admin
from django.http import HttpResponseRedirect, HttpResponseForbidden
from django.urls import path, reverse
from django.utils import timezone

from utils.utils_class_mixins import UserLinkMixin, PageLinkMixin, PostLinkMixin, YearFilter
from .models import VisitorGeoData, VisitorPageData, ViewedPost, UserInteraction

logger = logging.getLogger(__name__.split('.')[0])


@admin.register(ViewedPost)
class ViewedPostAdmin(PostLinkMixin, admin.ModelAdmin):
    list_display = ['id', 'post_link', 'timestamp', 'ip_address']
    list_filter = ['post']
    search_fields = ['timestamp', 'ip_address']
    change_list_template = 'admin/viewedpost_change_list.html'

    def get_urls(self):
        my_urls = [
            path('purge_old_views/', self.purge_old_views, name='purge_old_views')
        ]
        return my_urls + super().get_urls()

    def purge_old_views(self, request):
        if not request.user.has_perm('analytics.delete_viewedpost'):
            return HttpResponseForbidden('You do not have permission to perform this action.')

        logger.warning(f'purge_old_views action called by {request.user}')
        time_threshold = timezone.now() - timedelta(hours=24)
        old_records = ViewedPost.objects.filter(timestamp__lte=time_threshold)
        count = old_records.count()
        old_records.delete()
        self.message_user(request, f'Successfully deleted {count} old records')
        return HttpResponseRedirect(reverse('admin:analytics_viewedpost_changelist'))


class VisitorGeoDataYearFilter(YearFilter):
    data_field = 'timestamp'


@admin.register(VisitorGeoData)
class VisitorGeoDataAdmin(UserLinkMixin, admin.ModelAdmin):
    list_display = ['id', 'user_link', 'ip_address', 'ip_location', 'timestamp']
    list_filter = ['country', VisitorGeoDataYearFilter]
    search_fields = ['user', 'ip_address', 'country', 'city']
    readonly_fields = ['id', 'user', 'ip_address', 'country', 'city', 'timestamp']

    def ip_location(self, obj):
        if obj.country and obj.city:
            return f'{obj.country} - {obj.city}'
        return '-'

    ip_location.short_description = 'IP Location'

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm('analytics.change_visitorgeodata'):
            return []
        return self.readonly_fields


@admin.register(VisitorPageData)
class VisitorPageDataAdmin(UserLinkMixin, PageLinkMixin, admin.ModelAdmin):
    list_display = ['id', 'user_link', 'ip_address', 'timestamp', 'page_link']
    list_filter = [VisitorGeoDataYearFilter]
    search_fields = ['user', 'ip_address', 'page']
    readonly_fields = ['id', 'user', 'ip_address', 'timestamp', 'page']

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm('analytics.change_visitorpagedata'):
            return []
        return self.readonly_fields


@admin.register(UserInteraction)
class UserInteractionAdmin(PageLinkMixin, admin.ModelAdmin):
    list_display = ['id', 'interaction_type', 'x_coordinate', 'y_coordinate', 'timestamp', 'page_link']
    list_filter = [VisitorGeoDataYearFilter]
    search_fields = ['interaction_type', 'page']
    readonly_fields = ['id', 'interaction_type', 'x_coordinate', 'y_coordinate', 'timestamp', 'page']

    def get_readonly_fields(self, request, obj=None):
        if request.user.has_perm('analytics.change_userinteraction'):
            return []
        return self.readonly_fields
