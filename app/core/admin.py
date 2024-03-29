"""adding models in admin panel"""
from django.contrib import admin # noqa
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from core import models

# Register your models here.


class UserAdmin(BaseUserAdmin):
    """create good view of model"""

    ordering = ['id']
    list_display = ['email', 'name', 'is_staff', 'is_superuser', ]
    list_editable = ['is_staff', 'is_superuser', ]
    fieldsets = (
            (_('Main information'),
                {'fields': ('email', 'password')}),
            (_('permission'),
                {'fields': ('is_active', 'is_staff', 'is_superuser')}),
            (_('important dates'),
                {'fields': ('last_login',)}),
            )
    readonly_fields = ['last_login']
    add_fieldsets = (
            (
                _('add new user'), {
                    'classes': ('wide',),
                    'fields': (
                        'email',
                        'name',
                        'password1',
                        'password2',
                        'is_active',
                        'is_staff',
                        'is_superuser'
                        )
                    }),
            )


admin.site.register(models.User, UserAdmin)


admin.site.register(models.Recipe)
admin.site.register(models.Tag)
