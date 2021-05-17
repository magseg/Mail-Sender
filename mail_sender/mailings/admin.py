from django.contrib import admin

from .models import HTMLTemplate, AddresseeList, Addressee, Unsubscriber, SenderHistory


@admin.register(HTMLTemplate)
class HTMLTemplateAdmin(admin.ModelAdmin):
    pass


@admin.register(AddresseeList)
class AddresseeListAdmin(admin.ModelAdmin):
    pass


@admin.register(Addressee)
class AddresseeAdmin(admin.ModelAdmin):
    pass


@admin.register(Unsubscriber)
class UnsubscriberAdmin(admin.ModelAdmin):
    pass


@admin.register(SenderHistory)
class SenderHistoryAdmin(admin.ModelAdmin):
    pass
