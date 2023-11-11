from django.contrib import admin, messages
from .models import UnbanRequest, CustomUser
from django.db import transaction, DatabaseError


@admin.register(UnbanRequest)
class UnbanRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['id', 'username', 'full_name', 'is_staff', 'is_banned']
    list_filter = ['is_staff', 'is_banned']
    search_fields = ['username', 'full_name']
    readonly_fields = ['date_joined', 'last_login']
    actions = ['ban_user']

    def full_name(self, obj):
        if obj.first_name and obj.last_name:
            return f'{obj.first_name} {obj.last_name}'
        return '-'
    full_name.short_description = 'Full name'

    def ban_user(self, request, queryset):
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
                        print(f'Error banning user {user}: {e}')
    ban_user.short_description = 'Ban selected users'

