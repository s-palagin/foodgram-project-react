from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        'pk',
        'username',
        'email',
        'first_name',
        'last_name',
        'role',
    )
    exclude = (
        'date_joined',
        'last_login',
        'groups',
        'user_permissions',
    )
    list_filter = ('email', 'username')
    search_fields = ('username',)
    empty_value_display = '(пуcто)'

    def get_form(self, request, obj=None, change=False, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        is_admin = request.user.is_admin

        if not is_admin:
            for field in form.base_fields:
                form.base_fields[field].disabled = True

        return form
