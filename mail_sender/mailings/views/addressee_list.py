from django.db.models import Count
from django.shortcuts import render
from django.utils.decorators import decorator_from_middleware
from django.urls import reverse

from core.middlewares import IsAuthenticatedMiddleware
from core.utils import generate_breadcumbs, get_russian_countable_name

from ..commands import UploadAddresseeList, DeleteAddresseeLists
from ..models import AddresseeList


@decorator_from_middleware(IsAuthenticatedMiddleware)
def addressee_list(request):
    this_page_url = reverse('addressee_lists')
    file_upload_errors = []
    files_uploaded = 0
    file_upload_success_message = None
    delete_errors = []
    delete_successful_message = None

    if request.method == 'POST' and request.FILES and 'addressee_list' in request.FILES.keys():
        data = request.FILES.getlist('addressee_list')
        for datum in data:
            uploaded_count, uploaded_errors = UploadAddresseeList(request.user.id, datum).execute()
            files_uploaded += uploaded_count
            file_upload_errors += uploaded_errors
        if files_uploaded:
            file_upload_success_message = '{} email {}.'.format(
                files_uploaded,
                get_russian_countable_name(
                    files_uploaded,
                    item_1='загружен',
                    item_4='загружены',
                    item_5='загружено',
                )
            )
    elif request.method == 'POST' and not request.FILES and 'addressee_lists' in request.POST.keys():
        data = request.POST.getlist('addressee_lists')
        delete_count, delete_errors = DeleteAddresseeLists(request.user.id, data).execute()
        if not delete_errors:
            delete_successful_message = '{} {} {}.'.format(
                delete_count,
                get_russian_countable_name(
                    delete_count,
                    item_1='список адресов',
                    item_4='списка адресов',
                    item_5='списков адресов',
                ),
                get_russian_countable_name(
                    delete_count,
                    item_1='удален',
                    item_4='удалены',
                    item_5='удалено',
                )
            )

    return render(
        request,
        'addressee_lists/list.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/profile', 'title': 'Профиль'},
                {'url': this_page_url, 'title': 'Мои адресаты'},
            ]),
            'addressee_lists': AddresseeList.objects.filter(
                is_published=True,
                profile=request.user.profile,
            ).annotate(
                addressee_count=Count('addressees'),
            ).order_by('-created_at'),
            'delete_url': this_page_url,
            'upload_url': this_page_url,
            'file_upload_errors': file_upload_errors,
            'file_upload_success_message': file_upload_success_message,
            'delete_errors': delete_errors,
            'delete_successful_message': delete_successful_message,
            'base_addressee_small_list_url': reverse('addressee_small_list', kwargs={'addressee_list_id': 0})[:-1]
        }
    )
