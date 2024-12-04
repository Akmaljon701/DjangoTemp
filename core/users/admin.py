from django.contrib import admin
from django.contrib.admin import ModelAdmin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from core.users import models

admin.site.site_title = "Reserveit Admin"
admin.site.site_header = "Reserveit"
admin.site.index_title = "Reserveit Admin"
admin.site.site_brand = "Reserveit"
admin.site.welcome_sign = "Reserveit"
admin.site.copyright = "Reserveit"

admin.site.unregister(Group)


@admin.register(models.User)
class CustomUserAdmin(UserAdmin):
    list_display = ('phone', 'full_name', 'email', 'role', 'is_active', 'is_staff')
    search_fields = ('phone', 'full_name', 'email')
    ordering = ('phone',)
    fieldsets = (
        (None, {'fields': ('phone', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'email', 'date_of_birth', 'role', 'device_tokens')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login',)}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('phone', 'password1', 'password2', 'full_name', 'email', 'date_of_birth', 'role', 'is_active', 'is_staff'),
        }),
    )
