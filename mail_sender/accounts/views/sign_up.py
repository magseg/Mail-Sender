from django import forms
from django.conf import settings
from django.contrib.auth.forms import UserCreationForm, UsernameField
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.shortcuts import render, redirect
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from core.tasks import send_email_to_admin_async
from core.utils import generate_breadcumbs, get_uuid_string


class CustomSignUpForm(UserCreationForm):
    error_messages = {
        'password_mismatch': _("Пароли не совпадают."),
        'invalid_email': _("Неверный формат email."),
        'user_with_email_exists': _("Пользователь с таким email уже существует."),
        'first_name_empty': _("Поле Имя не может быть пустым."),
        'last_name_empty': _("Поле Фамилия не может быть пустым."),
    }

    first_name = forms.CharField(
        strip=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
    )

    last_name = forms.CharField(
        strip=False,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True,
    )

    username = UsernameField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'hidden'}),
        initial=get_uuid_string(),
        required=True,
    )

    email = forms.EmailField(
        max_length=254,
        widget=forms.EmailInput(attrs={'autofocus': True, 'class': 'form-control', 'type': 'email'}),
        required=True,
    )

    password1 = forms.CharField(
        strip=True,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        required=True,
    )

    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=True,
        required=True,
    )

    class Meta:
        model = User
        field_classes = {'username': UsernameField}
        fields = ('username', 'email', 'password1', 'password2', 'first_name', 'last_name')

    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name", '').strip()
        if len(first_name) == 0:
            raise forms.ValidationError(
                self.error_messages['first_name_empty'],
                code='first_name_empty',
            )
        return first_name

    def clean_last_name(self):
        last_name = self.cleaned_data.get("last_name", '').strip()
        if len(last_name) == 0:
            raise forms.ValidationError(
                self.error_messages['last_name_empty'],
                code='last_name_empty',
            )
        return last_name

    def clean_email(self):
        email = self.cleaned_data.get("email") or ''
        try:
            EmailValidator().__call__(email)
        except ValidationError:
            raise forms.ValidationError(
                self.error_messages['invalid_email'],
                code='invalid_email',
            )
        if User.objects.filter(email=self.cleaned_data.get("email")).exists():
            raise forms.ValidationError(
                self.error_messages['user_with_email_exists'],
                code='user_with_email_exists',
            )
        return email


def signup(request):
    if request.method == 'POST':
        form = CustomSignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.username = get_uuid_string()
            user.first_name = form.cleaned_data.get('first_name', '')
            user.last_name = form.cleaned_data.get('last_name', '')
            user.email = form.cleaned_data.get('email')
            user.is_active = False
            user.save()
            user.refresh_from_db()
            user.save()

            send_email_to_admin_async.apply_async(
                (
                    'Зарегистрирован <a href="{}">новый аккаунт</a> на сайте <a href="{}">{}</a>'.format(
                        settings.HTTP_DOMAIN + reverse('admin:{}_{}_change'.format(
                            User._meta.app_label,
                            User._meta.model_name
                        ), args=(user.id,)),
                        settings.HTTP_DOMAIN,
                        settings.HTTP_DOMAIN,
                    ),
                    'Регистрация в сервисе mail-sender',
                ),
            )
            return redirect('account_is_registered')
    else:
        form = CustomSignUpForm()
    return render(
        request,
        'pages/signup.html',
        {
            'form': form,
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/signup', 'title': 'Регистрация'},
            ])
        }
    )
