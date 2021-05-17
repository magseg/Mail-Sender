from django.db.models import Count
from django.shortcuts import render
from django.urls import reverse
from django.utils.decorators import decorator_from_middleware

from core.middlewares import IsAuthenticatedMiddleware
from core.utils import generate_breadcumbs

from accounts.models import EmailAccount


@decorator_from_middleware(IsAuthenticatedMiddleware)
def unsubscribers_all(request):
    return render(
        request,
        'mailings/unsubscribers_all.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/profile', 'title': 'Профиль'},
                {'url': '', 'title': 'Отписавшиеся от рассылки'},
            ]),
            'accounts': EmailAccount.objects.filter(
                profile=request.user.profile,
                is_published=True,
            ).annotate(
                unsubscribers_count=Count('unsubscriber'),
            ).select_related(
                'common_smtp',
                'custom_smtp',
            ),
            'item_url': reverse('unsubscribers_list', kwargs={'email_account_id': 0})[:-1]
        }
    )
