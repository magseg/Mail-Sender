from django.http import Http404
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse

from core.utils import generate_breadcumbs

from accounts.models import EmailAccount
from ..commands import Unsubscribe


@csrf_exempt
def unsubscribe(request, unsubscribe_key):
    try:
        email_account = EmailAccount.objects.get(unsubscribed_key=unsubscribe_key)
    except (EmailAccount.DoesNotExist, EmailAccount.MultipleObjectsReturned):
        raise Http404

    unsubscribe_errors = []

    if request.method == 'POST' and 'email' in request.POST.keys():
        unsubscribe_errors += Unsubscribe(
            request.POST.get('email'),
            email_account.id,
            request.POST.get('reason', ''),
        ).execute()
        if not unsubscribe_errors:
            return redirect('unsubscribe_done')

    return render(
        request,
        'mailings/unsubscribe_page.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '', 'title': 'Отписаться от получения информационных писем от {}'.format(email_account.email)},
            ]),
            'unsubscribe_url': reverse('unsubscribe', kwargs={
                'unsubscribe_key': email_account.unsubscribed_key,
            }),
        }
    )
