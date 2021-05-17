from django.urls import path, include

from .views import email_account_list, email_account_create, email_account_item, get_email_account_preupdate_message

urlpatterns = [
    path('<int:email_account_id>', email_account_item, name='email_account_item'),
    path('create', email_account_create, name='email_account_create'),
    path('list', email_account_list, name='email_account_list'),
    path('preupdate_message', get_email_account_preupdate_message, name='email_account_preupdate_message'),
]
