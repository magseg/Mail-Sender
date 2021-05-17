import functools

from django.conf import settings
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.decorators import decorator_from_middleware
from django.urls import reverse

from core.middlewares import IsAuthenticatedMiddleware
from core.utils import generate_breadcumbs, get_russian_countable_name
from mailings.models import Unsubscriber

from ..commands import UpdateEmailAccount, DeleteEmailAccount
from ..models import EmailAccount


@decorator_from_middleware(IsAuthenticatedMiddleware)
def email_account_item(request, email_account_id):
    try:
        email_account = EmailAccount.objects.get(
            id=email_account_id,
            profile=request.user.profile,
            is_published=True,
        )
    except EmailAccount.DoesNotExist:
        raise Http404

    list_url = reverse('email_account_list')
    this_url = reverse('email_account_item', kwargs={'email_account_id': email_account_id})
    update_errors = []
    updated = False

    if request.method == 'POST' and functools.reduce(
        lambda x, y: x and y in request.POST.keys(),
        ['password', 'smtp_port', 'smtp_host'],
        True
    ):
        updated, email_account, update_errors = UpdateEmailAccount(
            request.user.id,
            email_account_id,
            new_smtp_host=request.POST.get('smtp_host'),
            new_smtp_port=request.POST.get('smtp_port'),
            new_password=request.POST.get('password'),
        ).execute()
    elif request.method == 'POST' and 'account' in request.POST.keys():
        delete_errors = DeleteEmailAccount(request.user.id, email_account_id).execute()
        if not delete_errors:
            response = redirect('email_account_list')
            response['Location'] += '?successdelete=success'
            return response
        update_errors += delete_errors

    unsubscribers_count = Unsubscriber.objects.filter(email_account=email_account).count()

    return render(
        request,
        'email_accounts/item.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/profile', 'title': 'Профиль'},
                {'url': list_url, 'title': 'Мои почты для рассылки'},
                {'url': '', 'title': email_account.email},
            ]),
            'delete_url': this_url,
            'email_account': email_account,
            'preupdate_message_url': reverse('email_account_preupdate_message'),
            'update_url': this_url,
            'update_errors': update_errors,
            'updated': updated,
            'unsubscribe_link': settings.HTTP_DOMAIN + reverse('unsubscribe', kwargs={
                'unsubscribe_key': email_account.unsubscribed_key,
            }),
            'unsubscribe_message': 'Нет отписок от аккаунта.'
            if unsubscribers_count == 0 else 'От этого аккаунта {} <b><a href="{}">{} {}</a></b>.'.format(
                get_russian_countable_name(
                    unsubscribers_count,
                    item_1='отписался',
                    item_4='отписались',
                    item_5='отписалось',
                ),
                reverse('unsubscribers_list', kwargs={'email_account_id': email_account_id}),
                unsubscribers_count,
                get_russian_countable_name(
                    unsubscribers_count,
                    item_1='контакт',
                    item_4='контакта',
                    item_5='контактов',
                ),
            ),
        }
    )
