from django.shortcuts import render
from django.utils.decorators import decorator_from_middleware
from django.urls import reverse

from core.middlewares import IsAuthenticatedMiddleware

from core.utils import generate_breadcumbs, get_russian_countable_name
from mailings.commands import UploadHTMLTemplate, DeleteHTMLTemplates
from mailings.models import HTMLTemplate


@decorator_from_middleware(IsAuthenticatedMiddleware)
def html_templates_list(request):
    this_page_url = reverse('html_templates_list')
    file_upload_errors = []
    files_uploaded = 0
    file_upload_success_message = None
    files_delete_errors = []
    files_deleted = 0
    files_delete_message = None

    if request.method == 'POST' and not request.FILES and 'html_templates' in request.POST.keys():
        data = request.POST
        deleted_count, delete_errors = DeleteHTMLTemplates(request.user.id, data.getlist('html_templates')).execute()
        files_delete_errors += delete_errors
        files_deleted += deleted_count
        if files_deleted:
            files_delete_message = '{} {} {}.'.format(
                deleted_count,
                get_russian_countable_name(
                    deleted_count,
                    item_1='файл',
                    item_4='файла',
                    item_5='файлов',
                ),
                get_russian_countable_name(
                    deleted_count,
                    item_1='удален',
                    item_4='удалены',
                    item_5='удалено',
                )
            )
    elif request.FILES and 'html_template' in request.FILES.keys():
        data = request.FILES.getlist('html_template')
        for datum in data:
            uploaded_count, uploaded_errors = UploadHTMLTemplate(request.user.id, datum).execute()
            files_uploaded += uploaded_count
            file_upload_errors += uploaded_errors
        if files_uploaded:
            file_upload_success_message = '{} {} {}.'.format(
                files_uploaded,
                get_russian_countable_name(
                    files_uploaded,
                    item_1='файл',
                    item_4='файла',
                    item_5='файлов',
                ),
                get_russian_countable_name(
                    files_uploaded,
                    item_1='загружен',
                    item_4='загружены',
                    item_5='загружено',
                )
            )

    return render(
        request,
        'html_files/list.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/profile', 'title': 'Профиль'},
                {'url': this_page_url, 'title': 'Мои HTML-шаблоны'},
            ]),
            'html_templates_list': HTMLTemplate.objects.filter(
                profile_id=request.user.profile,
                is_published=True,
            ).order_by('-created_at'),
            'delete_url': this_page_url,
            'upload_url': this_page_url,
            'file_upload_errors': file_upload_errors,
            'file_upload_success_message': file_upload_success_message,
            'files_delete_message': files_delete_message,
            'files_delete_errors': files_delete_errors,
            'html_template_get_json_url': reverse('html_templates_get_json'),
        }
    )
