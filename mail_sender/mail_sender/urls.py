from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include

from accounts.views import (
    account_is_registered, login, logout, profile, password_reset_api, password_reset_view, password_reset_done_view,
    signup, password_reset_confirm_view, password_reset_complete_view,
)
from api.mailing.views import SendMailingAPI
from core.views import index, faq, favicon, faq_ask, api_docs, feedback, feedback_done

import accounts.email_account_urls as email_account_urls
import mailings.urls as mailings_urls
from .views import yandex_view


urlpatterns = [
    path('admin/', admin.site.urls),

    path('login', login, name='login'),
    path('logout', logout, name='logout'),
    path('signup', signup, name='signup'),
    path('password_reset_api', password_reset_api, name='password_reset_api'),
    path('profile', profile, name='profile'),
    path('account_is_registered', account_is_registered, name='account_is_registered'),

    path('password_reset/', password_reset_view, name='password_reset'),
    path('password_reset/done/', password_reset_done_view, name='password_reset_done'),
    path('reset/<str:uidb64>/<str:token>/', password_reset_confirm_view, name='password_reset_confirm'),
    path('reset/done/', password_reset_complete_view, name='password_reset_complete'),

    path('email_accounts/', include(email_account_urls), name='email_accounts'),
    path('mailings/', include(mailings_urls), name='mailings'),

    path('external-mailing', SendMailingAPI.as_view(), name='api_send_mailing'),

    path('api-documentation', api_docs, name='api_docs'),
    path('faq', faq, name='faq'),
    path('feedback', feedback, name='feedback'),
    path('feedback-done', feedback_done, name='feedback_done'),
    path('faq-ask', faq_ask, name='faq_ask'),
    path('favicon.ico', favicon, name='favicon'),
    path('yandex/', yandex_view, name='yandex_maps'),
    path('', index, name='main'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = 'mail_sender.views.handler404'
handler403 = 'mail_sender.views.handler403'
handler400 = 'mail_sender.views.handler400'
handler500 = 'mail_sender.views.handler500'
