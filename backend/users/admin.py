from django.contrib import admin
from django.contrib.auth.models import Group

from .models import Follow, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'date_joined',
        'first_name',
        'last_name',
        'role',
    )
    exclude = (
        'last_login',
        'groups',
        'user_permissions',
        'is_staff',
        'is_superuser'
    )
    list_filter = ('email', 'username')
    search_fields = ('username',)

    def save_model(self, request, obj, form, change):
        if obj.pk:
            if 'pbkdf2_sha256$' not in obj.password:
                obj.set_password(obj.password)
            obj.is_staff = True if obj.role == 'admin' else False
            obj.is_superuser = True if obj.role == 'admin' else False
        obj.save()


@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    list_display = ('pk', 'user', 'author')
    list_filter = ('user', 'author')
    search_fields = ('author',)


admin.site.unregister(Group)
