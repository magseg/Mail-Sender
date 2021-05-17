from django.contrib import admin

from .models import FAQ, ClientQuestion, Feedback


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'is_published', )
    list_filter = ('is_published', )


@admin.register(Feedback)
class FeedbackAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'


@admin.register(ClientQuestion)
class ClientQuestionAdmin(admin.ModelAdmin):
    date_hierarchy = 'created_at'
    list_display = ('__str__', 'question', 'answer', )

    def get_queryset(self, request):
        return super().get_queryset(request=request).order_by('-created_at')
