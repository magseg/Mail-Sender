from django.contrib import admin

from .models import CustomSMTPServer, CommonSMTPServer


@admin.register(CommonSMTPServer)
class CommonSMTPServerAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'is_published', )
    list_filter = ('is_published', )


@admin.register(CustomSMTPServer)
class CustomSMTPServerAdmin(admin.ModelAdmin):
    list_display = ('host', 'port', 'is_published', )
    list_filter = ('is_published', )
