from django.contrib import admin


from .models import Profile, EmailAccount


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'email', 'is_confirmed', )
    list_filter = ('is_confirmed', )

    def get_readonly_fields(self, request, obj=None):
        readonly_list = ['user']
        if obj and hasattr(obj, 'user') and obj.user.is_staff:
            readonly_list += ['is_confirmed']
        return readonly_list

    def get_queryset(self, request):
        return super().get_queryset(request=request).select_related('user')

    def first_name(self, obj):
        return None if not obj.user else obj.user.first_name
    first_name.short_description = 'Имя'

    def last_name(self, obj):
        return None if not obj.user else obj.user.last_name
    last_name.short_description = 'Имя'

    def email(self, obj):
        return None if not obj.user else obj.user.email
    email.short_description = 'Email'


@admin.register(EmailAccount)
class EmailAccountAdmin(admin.ModelAdmin):
    list_display = ('email', 'profile', 'show_password', 'smtp_host', 'smtp_port', 'is_published', )
    list_filter = ('is_published', )

    def smtp_port(self, obj):
        return obj.get_smtp_port() if obj else None
    smtp_port.short_description = 'SMTP-порт'

    def smtp_host(self, obj):
        return obj.get_smtp_host() if obj else None
    smtp_host.short_description = 'SMTP-сервер'

    def show_password(self, obj):
        return obj.get_password()
    show_password.short_description = 'Пароль'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False

    def get_queryset(self, request):
        return super().get_queryset(request=request).prefetch_related(
            'profile',
            'common_smtp',
            'custom_smtp',
        )
