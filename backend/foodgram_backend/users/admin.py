from django.contrib import admin

from users.models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'first_name',
        'last_name',
        'username',
        'email',
        'role',
    )
    list_filter = ('first_name', 'email')
    empty_value_display = '-пусто-'
    list_editable = (
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
    )
