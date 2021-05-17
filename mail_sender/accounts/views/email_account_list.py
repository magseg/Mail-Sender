from django.db.models import Count
from django.utils.decorators import decorator_from_middleware
from django.shortcuts import render
from django.urls import reverse

from core.middlewares import IsAuthenticatedMiddleware
from core.utils import generate_breadcumbs, get_russian_countable_name

from ..commands import DeleteEmailAccounts
from ..models import EmailAccount


@decorator_from_middleware(IsAuthenticatedMiddleware)
def email_account_list(request):
    this_view_url = reverse('email_account_list')
    delete_errors = []
    delete_message = None

    if request.GET.get('successdelete', None):
        delete_message = 'Аккаунт успешно удалён.'

    if request.method == 'POST':
        data = request.POST
        if 'accounts' in data.keys():
            email_accounts_delete_count, email_account_delete_errors = DeleteEmailAccounts(
                request.user.id,
                data.getlist('accounts'),
            ).execute()
            delete_errors += email_account_delete_errors
            if email_accounts_delete_count:
                delete_message = '{} {} {}.'.format(
                    email_accounts_delete_count,
                    get_russian_countable_name(
                        email_accounts_delete_count,
                        item_1='аккаунт',
                        item_4='аккаунта',
                        item_5='аккаунтов'
                    ),
                    get_russian_countable_name(
                        email_accounts_delete_count,
                        item_1='удален',
                        item_4='удалено',
                        item_5='удалены'
                    ),
                )

    return render(
        request,
        'email_accounts/list.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/profile', 'title': 'Профиль'},
                {'url': this_view_url, 'title': 'Мои почты для рассылки'},
            ]),
            'add_url': reverse('email_account_create'),
            'delete_url': this_view_url,
            'success_create': bool(request.GET.get('success', False)),
            'success_delete_message': delete_message,
            'delete_errors': delete_errors,
            'smtp_list': EmailAccount.objects.filter(
                profile__user=request.user,
                is_published=True,
            ).select_related(
                'common_smtp',
                'custom_smtp',
            ).annotate(
                unsubscriber_count=Count('unsubscriber'),
            ).order_by('id'),
            'email_account_item_url': reverse('email_account_item', kwargs={'email_account_id': 0})[:-1],
        }
    )
