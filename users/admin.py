import logging

from django.contrib import admin, messages
from django.db import transaction, DatabaseError
from django.urls import reverse
from django.utils.html import format_html

from .models import UnbanRequest, CustomUser, EmailSubscriber
from utils.utils_class_mixins import UserLinkMixin, YearFilter

logger = logging.getLogger(__name__.split('.')[0])


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'full_name', 'is_staff', 'is_banned', 'group_link']
    list_filter = ['is_staff', 'is_banned', YearFilter]
    search_fields = ['username', 'full_name']
    readonly_fields = [
        'username', 'first_name', 'last_name', 'email', 'date_joined', 'last_login', 'is_superuser', 'is_staff',
        'is_active', 'user_permissions', 'groups', 'is_banned'
    ]
    exclude = ['password']
    actions = ['ban_user', 'unban_user']

    def full_name(self, obj):
        if obj.first_name and obj.last_name:
            return f'{obj.first_name} {obj.last_name}'
        return '-'

    full_name.short_description = 'Full name'

    def group_link(self, obj):
        return format_html(
            ', '.join([f'<a href="{reverse("admin:auth_group_change", args=[group.pk])}">{group.name}</a>' for group in
                       obj.groups.all()])
        )

    group_link.short_description = 'Group(s)'

    def ban_user(self, request, queryset):
        logger.warning(f'ban_user action called by {request.user}')
        with transaction.atomic():
            for user in queryset:
                if user.is_banned:
                    messages.warning(request, f'User {user} already banned')
                else:
                    try:
                        user.is_banned = True
                        user.save()
                        messages.success(request, f'Banned user {user}')
                    except DatabaseError as e:
                        logger.error(f'Error banning user {user}: {e}')

    ban_user.short_description = 'Ban selected users'

    def unban_user(self, request, queryset):
        logger.warning(f'unban_user action called by {request.user}')
        with transaction.atomic():
            for user in queryset:
                if not user.is_banned:
                    messages.warning(request, f'User {user} not banned')
                else:
                    try:
                        user.is_banned = False
                        user.save()
                        messages.success(request, f'Unbanned user {user}')
                    except DatabaseError as e:
                        logger.error(f'Error unbanning user {user}: {e}')

    unban_user.short_description = 'Unban selected users'

    def get_readonly_fields(self, request, obj=None):
        if request.user.is_superuser:
            return []
        return self.readonly_fields

    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.has_perm('users.change_customuser'):
            return actions
        return []


class UnbanRequestYearFilter(YearFilter):
    data_field = 'created_at'


@admin.register(UnbanRequest)
class UnbanRequestAdmin(UserLinkMixin, admin.ModelAdmin):
    list_display = ['id', 'user_link', 'created_at', 'status']
    list_filter = ['status', UnbanRequestYearFilter]
    search_fields = ['user', 'content']


@admin.register(EmailSubscriber)
class EmailSubscriberAdmin(UserLinkMixin, admin.ModelAdmin):
    list_display = ['id', 'user_link']
    search_fields = ['user']
