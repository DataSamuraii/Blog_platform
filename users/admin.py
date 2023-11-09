from django.contrib import admin
from .models import UnbanRequest, CustomUser


@admin.register(UnbanRequest)
class UnbanRequestAdmin(admin.ModelAdmin):
    pass


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass
