from django.shortcuts import render

from core.utils import generate_breadcumbs


def unsubscribe_done(request):
    return render(
        request,
        'mailings/unsubscribe_done.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '', 'title': 'Отписка от рассылки'},
            ]),
        }
    )
