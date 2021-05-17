from django.shortcuts import render
from django.utils.decorators import decorator_from_middleware
from django.urls import reverse

from core.middlewares import IsAuthenticatedMiddleware
from core.utils import generate_breadcumbs

from ..models import SenderHistory


@decorator_from_middleware(IsAuthenticatedMiddleware)
def mailing_history(request):
    sender_history = SenderHistory.objects.filter(
        profile=request.user.profile,
    ).select_related('email_account').order_by('-created_at')

    return render(
        request,
        'mailings/history.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/profile', 'title': 'Профиль'},
                {'url': '', 'title': 'Мои рассылки'},
            ]),
            'sender_history': sender_history,
            'history_item_url': reverse('mailing_history_item', kwargs={'history_item_id': 0})[:-1]
        }
    )
