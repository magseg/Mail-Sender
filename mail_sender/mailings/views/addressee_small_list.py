from django.http import Http404
from django.shortcuts import render
from django.utils.decorators import decorator_from_middleware
from django.urls import reverse

from core.middlewares import IsAuthenticatedMiddleware
from core.utils import generate_breadcumbs
from ..models import AddresseeList, Addressee, Unsubscriber


@decorator_from_middleware(IsAuthenticatedMiddleware)
def addressee_small_list(request, addressee_list_id):
    try:
        addressee_list = AddresseeList.objects.get(id=addressee_list_id, is_published=True)
    except AddresseeList.DoesNotExist:
        raise Http404

    list_url = reverse('addressee_lists')

    addressees = Addressee.objects.filter(addressee_list=addressee_list).order_by('email').values('email')
    unsubscribers = Unsubscriber.objects.filter(
        email__in=addressees,
        email_account__profile=request.user.profile,
    ).values('email', 'email_account__email', ).order_by('email')

    addressee_list_new = list()
    i = 0
    total = len(unsubscribers)
    for addressee in addressees:
        addressee_obj = {'email': addressee['email'], 'email_accounts': []}
        while i < total and unsubscribers[i]['email'] <= addressee['email']:
            if unsubscribers[i]['email'] == addressee['email']:
                addressee_obj['email_accounts'].append(unsubscribers[i]['email_account__email'])
            i += 1
        addressee_obj['email_accounts'] = ', '.join(addressee_obj['email_accounts']) or '-'
        addressee_list_new.append(addressee_obj)

    return render(
        request,
        'addressee_lists/small_list.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/profile', 'title': 'Профиль'},
                {'url': list_url, 'title': 'Мои адресаты'},
                {'url': '', 'title': 'Список адресатов {}'.format(addressee_list.name)},
            ]),
            'addressee_small_list': addressee_list_new,
        }
    )
