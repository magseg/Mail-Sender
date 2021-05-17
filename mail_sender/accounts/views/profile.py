from functools import reduce

from django.shortcuts import render
from django.utils.decorators import decorator_from_middleware
from django.urls import reverse

from core.middlewares import IsAuthenticatedMiddleware
from core.utils import generate_breadcumbs

from ..commands import ChangeUserPassword, ChangeUserInfo


@decorator_from_middleware(IsAuthenticatedMiddleware)
def profile(request):
    context = {
        'breadcumb': generate_breadcumbs([
            {'url': '/', 'title': 'Главная'},
            {'url': '/profile', 'title': 'Профиль'},
        ]),
        'profile_url': reverse('profile'),
        'errors': {
            'change_password': [],
            'edit_profile': [],
        },
        'success': {
            'change_password': [],
            'edit_profile': [],
        },
    }

    if request.method == 'POST':
        data = request.POST
        if reduce(lambda x, y: x and (y in data.keys()), ['old_password', 'new_password_1', 'new_password_2'], True):
            errors = ChangeUserPassword(
                request.user.id,
                request.POST.get('old_password'),
                request.POST.get('new_password_1'),
                request.POST.get('new_password_2')
            ).execute()
            if errors:
                for error in errors:
                    context['errors']['change_password'].append(error)
            else:
                context['success']['change_password'].append('Пароль успешно сменён.')
        elif reduce(lambda x, y: x and (y in data.keys()), ['email', 'first_name', 'last_name'], True):
            errors = ChangeUserInfo(
                request.user.id,
                request.POST.get('first_name'),
                request.POST.get('last_name'),
                request.POST.get('email')
            ).execute()
            if errors:
                for error in errors:
                    context['errors']['edit_profile'].append(error)
            else:
                context['success']['edit_profile'].append('Данные успешно обновлены.')
                request.user.refresh_from_db()

    context['last_name'] = request.user.last_name
    context['first_name'] = request.user.first_name
    context['email'] = request.user.email

    return render(
        request,
        'accounts/profile.html',
        context=context,
    )
