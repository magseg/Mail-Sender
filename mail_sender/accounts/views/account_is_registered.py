from django.shortcuts import render

from core.utils import generate_breadcumbs


def account_is_registered(request):
    return render(
        request,
        'pages/account_is_registered.html',
        context={
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': 'account_is_registered', 'title': 'Завершение регистрации'},
            ])
        }
    )
