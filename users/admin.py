import logging

from django.contrib import admin, messages
from django.db import transaction, DatabaseError
from django.utils import timezone

from .models import UnbanRequest, CustomUser

logger = logging.getLogger(__name__.split('.')[0])


class YearFilter(admin.SimpleListFilter):
    title = 'year'
    parameter_name = 'year'
    data_field = 'date_joined'

    def lookups(self, request, model_admin):
        current_year = timezone.now().year
        return [(str(year), str(year)) for year in range(2020, current_year + 1)]

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(**{f'{self.data_field}__year': self.value()})
        return queryset


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'full_name', 'is_staff', 'is_banned']
    list_filter = ['is_staff', 'is_banned', YearFilter]
    search_fields = ['username', 'full_name']
    readonly_fields = ['date_joined', 'last_login']
    actions = ['ban_user']

    def full_name(self, obj):
        if obj.first_name and obj.last_name:
            return f'{obj.first_name} {obj.last_name}'
        return '-'

    full_name.short_description = 'Full name'

    def ban_user(self, request, queryset):
        logger.warning(f'ban_user action called by {request.user}')
        if not request.user.is_superuser:
            messages.error(request, 'Only superusers can perform this action.')
            return
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


class UnbanRequestYearFilter(YearFilter):
    data_field = 'created_at'


@admin.register(UnbanRequest)
class UnbanRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'status']
    list_filter = ['status', UnbanRequestYearFilter]
    search_fields = ['user', 'content']
    readonly_fields = ['user', 'created_at']
