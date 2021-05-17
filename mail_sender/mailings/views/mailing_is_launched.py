from django.shortcuts import render
from django.utils.decorators import decorator_from_middleware
from django.urls import reverse

from core.middlewares import IsAuthenticatedMiddleware
from core.utils import generate_breadcumbs


@decorator_from_middleware(IsAuthenticatedMiddleware)
def mailing_is_launched(request):
    return render(
        request,
        'mailings/has_been_created.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/profile', 'title': 'Профиль'},
                {'url': reverse('mailing_history'), 'title': 'Мои рассылки'},
                {'url': '', 'title': 'Новая'},
            ]),
        }
    )
