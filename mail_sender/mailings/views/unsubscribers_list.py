from django.http import Http404
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from core.middlewares import IsAuthenticatedMiddleware
from core.utils import generate_breadcumbs

from accounts.models import EmailAccount
from ..models import Unsubscriber


@decorator_from_middleware(IsAuthenticatedMiddleware)
def unsubscribers_list(request, email_account_id):
    try:
        email_account = EmailAccount.objects.get(id=email_account_id, is_published=True)
    except EmailAccount.DoesNotExist:
        raise Http404

    return render(
        request,
        'mailings/unsubscribers.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/profile', 'title': 'Профиль'},
                {'url': reverse('unsubscribers_all'), 'title': 'Отписавшиеся от рассылки'},
                {'url': '', 'title': 'Аккаунт {}'.format(email_account.email)},
            ]),
            'unsubscribers': Unsubscriber.objects.filter(
                email_account=email_account,
            ).order_by('-created_at'),
            'email_account': email_account,
        }
    )
