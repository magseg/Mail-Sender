from django.urls import path

from .views import (
    html_templates_list, addressee_list, create_mailing, mailing_is_launched, mailing_history, mailing_history_item,
    get_html_template_representation, unsubscribers_list, unsubscribers_all, unsubscribe, unsubscribe_done,
    addressee_small_list,
)

urlpatterns = [
    path('html-templates/list', html_templates_list, name='html_templates_list'),
    path('html-templates/get-json', get_html_template_representation, name='html_templates_get_json'),
    path('addressees/list', addressee_list, name='addressee_lists'),
    path('create', create_mailing, name='create_mailing'),
    path('launched', mailing_is_launched, name='mailing_is_launched'),
    path('history', mailing_history, name='mailing_history'),
    path('history/<int:history_item_id>', mailing_history_item, name='mailing_history_item'),
    path('unsubscribe/done', unsubscribe_done, name='unsubscribe_done'),
    path('unsubscribe/<str:unsubscribe_key>', unsubscribe, name='unsubscribe'),
    path('unsubscribers/all', unsubscribers_all, name='unsubscribers_all'),
    path('unsubscribers/list/<int:addressee_list_id>', addressee_small_list, name='addressee_small_list'),
    path('unsubscribers/<int:email_account_id>', unsubscribers_list, name='unsubscribers_list'),
]
