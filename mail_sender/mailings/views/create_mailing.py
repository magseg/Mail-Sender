from django.db.models import Count
from django.shortcuts import render, redirect
from django.utils.decorators import decorator_from_middleware
from django.urls import reverse

from accounts.models import EmailAccount
from core.middlewares import IsAuthenticatedMiddleware
from core.utils import generate_breadcumbs, get_russian_countable_name

from ..commands import GetListOfEmails, SendMailing
from ..models import AddresseeList, HTMLTemplate


@decorator_from_middleware(IsAuthenticatedMiddleware)
def create_mailing(request):
    # Ошибки
    create_errors = []

    # Обработка POST-запросов
    if request.method == 'POST':
        field_names = {
            'email_accounts_list': 'Почта для рассылки',
            'addressee_list': 'Список рассылки',
            'html_template': 'HTML-шаблон',
            'subject': 'Тема письма',
            'from': 'Имя отправителя',
        }
        try:
            email_account_id = request.POST.get('email_account')
            addressee_list_id = request.POST.get('addressee_list')
            html_template_id = request.POST.get('html_template')
            subject = request.POST.get('subject', '')
            fromname = request.POST.get('from', '')
            cooldown = request.POST.get('cooldown', 15)
            custom_addressee_list = request.POST.get('custom_addressee_list', '')
            sender_history_obj = None

            email_list, email_list_errors = GetListOfEmails(
                request.user.id,
                addressee_list_id,
                email_account_id,
                custom_addressee_list,
            ).execute()
            create_errors += email_list_errors

            if not create_errors:
                sending_errors, sender_history_obj = SendMailing(
                    request.user.id,
                    email_account_id,
                    email_list,
                    html_template_id,
                    subject,
                    fromname=fromname,
                    cooldown=cooldown,
                ).execute()
                create_errors += sending_errors

            if not create_errors:
                return redirect('mailing_is_launched')
        except KeyError as exc:
            create_errors.append('Параметр {} должен быть передан в POST-запросе.'.format(
                field_names[str(exc)]
            ))

    # Обработка GET-запросов или неудачных POST-запросов
    this_page_url = reverse('create_mailing')
    html_list_url = reverse('html_templates_list')
    addressees_list_url = reverse('addressee_lists')
    email_account_list_url = reverse('email_account_list')

    # Список Email-аккаунтов
    list_of_email_accounts = EmailAccount.objects.filter(
        is_published=True,
        profile=request.user.profile,
    )

    # Список адресатов
    list_of_addressee = []
    for addressee_list in AddresseeList.objects.filter(
        is_published=True,
        profile=request.user.profile,
    ).annotate(
        addressee_count=Count('addressees'),
    ).order_by('name'):
        list_of_addressee.append(
            {'key': addressee_list.id, 'value': '{} ({} {})'.format(
                addressee_list.name,
                addressee_list.addressee_count,
                get_russian_countable_name(
                    addressee_list.addressee_count,
                    item_1='получатель',
                    item_4='получателя',
                    item_5='получателей',
                )
            )}
        )
    list_of_addressee.append({'key': 0, 'value': 'Указать вручную'})

    # Список HTML-шаблонов
    list_of_html_templates = []
    for html_template in HTMLTemplate.objects.filter(
        is_published=True,
        profile=request.user.profile,
    ).order_by('name'):
        list_of_html_templates.append({'key': html_template.id, 'value': html_template.name})

    # Ответ
    return render(
        request,
        'mailings/create.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/profile', 'title': 'Профиль'},
                {'url': reverse('mailing_history'), 'title': 'Мои рассылки'},
                {'url': this_page_url, 'title': 'Новая'},
            ]),
            'list_of_addressee': list_of_addressee,
            'list_of_html_templates': list_of_html_templates,
            'list_of_email_accounts': list_of_email_accounts,
            'html_list_url': html_list_url,
            'addressees_list_url': addressees_list_url,
            'email_account_list_url': email_account_list_url,
            'form_create_url': this_page_url,
            'create_errors': create_errors,
        }
    )
