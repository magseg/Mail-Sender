from functools import reduce

from django import forms
from django.shortcuts import render, redirect
from django.utils.decorators import decorator_from_middleware
from django.urls import reverse

from core.middlewares import IsAuthenticatedMiddleware
from core.utils import generate_breadcumbs

from smtp.commands import CreateCustomSMTP
from smtp.models import CommonSMTPServer, CustomSMTPServer
from ..commands import CreateEmailAccount


class EmailAccountCreateForm(forms.Form):
    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['smtp'].choices = self.get_smtp_choices()

    def get_smtp_choices(self):
        acc = []
        for server in CommonSMTPServer.objects.filter(is_published=True):
            acc.append(
                ('common_{}'.format(server.id), server.name or server.host),
            )
        if hasattr(self.user, 'profile'):
            for server in CustomSMTPServer.objects.filter(is_published=True, profile=self.user.profile):
                acc.append(
                    ('custom_{}'.format(server.id), server.name or server.host),
                )
        acc.append(
            ('new', 'Добавить новый')
        )
        return acc

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'form-control'}),
    )

    password = forms.CharField(
        strip=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
    )

    smtp = forms.ChoiceField(
        choices=(),
        widget=forms.Select(attrs={'class': 'form-control'}),
    )

    smtp_host = forms.CharField(
        strip=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )

    smtp_port = forms.CharField(
        strip=False,
        widget=forms.NumberInput(attrs={'class': 'form-control', 'value': 0}),
        required=False,
    )

    smtp_name = forms.CharField(
        strip=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False,
    )


@decorator_from_middleware(IsAuthenticatedMiddleware)
def email_account_create(request):
    this_view_url = reverse('email_account_create')
    list_view_url = reverse('email_account_list')

    breadcumb = generate_breadcumbs([
        {'url': '/', 'title': 'Главная'},
        {'url': '/profile', 'title': 'Профиль'},
        {'url': list_view_url, 'title': 'Мои почты для рассылки'},
        {'url': this_view_url, 'title': 'Новая почта'},
    ])
    errors = []
    create_init = False

    if request.method == 'POST':
        data = request.POST
        if reduce(lambda x, y: x and (y in data.keys()), ['email', 'password', 'smtp'], True):
            create_init = True
            smtp_create = request.POST.get('smtp')
            common_smtp_id = None
            custom_smtp_id = None
            if smtp_create == 'new':
                custom_smtp, custom_smtp_create_errors = CreateCustomSMTP(
                    request.user.id,
                    smtp_host=request.POST.get('smtp_host', None),
                    smtp_port=request.POST.get('smtp_port', None),
                    smtp_name=request.POST.get('smtp_name', None),
                ).execute()
                errors += custom_smtp_create_errors
                custom_smtp_id = custom_smtp.id if custom_smtp else None
            elif smtp_create[:6] == 'common':
                try:
                    common_smtp_id = int(smtp_create[7:])
                except (TypeError, ValueError):
                    errors.append('Id SMTP-сервера должен быть в числовом формате')
            elif smtp_create[:6] == 'custom':
                try:
                    custom_smtp_id = int(smtp_create[7:])
                except (TypeError, ValueError):
                    errors.append('Id SMTP-сервера должен быть в числовом формате')
            else:
                errors.append('Непонятный id SMTP-сервера.')

            email_account, email_account_create_errors = CreateEmailAccount(
                request.user.id,
                request.POST.get('email'),
                request.POST.get('password'),
                common_smtp_id=common_smtp_id,
                custom_smtp_id=custom_smtp_id,
            ).execute()
            errors += email_account_create_errors

    if request.method == 'POST' and not errors and create_init:
        return redirect(list_view_url + '?success=success')
    else:
        return render(request, 'email_accounts/add.html', context={
            'form': EmailAccountCreateForm(request.user),
            'errors': errors,
            'breadcumb': breadcumb,
            'form_action': this_view_url,
        })
