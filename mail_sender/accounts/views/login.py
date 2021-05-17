from django import forms
from django.contrib.auth import authenticate, login as auth_login
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.views import LoginView
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from core.utils import generate_breadcumbs


class CustomAuthentificationForm(AuthenticationForm):

    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(attrs={'autofocus': True, 'class': 'form-control'}),
    )

    password = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )

    error_messages = {
        'invalid_login': _(
            "Пожалуйста, введите корректную пару имя пользователя и пароль."
            "Помните, что оба поля могут быть чувствительны к регистру."
        ),
        'inactive': _("Аккаунт не активирован."),
    }

    class Meta:
        fields = ('email', 'password',)

    def clean(self):
        email = self.cleaned_data.get('email') or ''
        password = self.cleaned_data.get('password')
        user = None
        username = None

        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            raise self.get_invalid_login_error()

        if username is not None and password:
            self.user_cache = authenticate(self.request, username=username, password=password)
            if self.user_cache is None:
                if user and user.is_active == False:
                    raise forms.ValidationError(
                        self.error_messages['inactive'],
                        code='inactive',
                    )
                raise self.get_invalid_login_error()

        if user.check_password(password) is False:
            raise self.get_invalid_login_error()

        self.cleaned_data['username'] = username
        return self.cleaned_data

    def is_valid(self):
        self.full_clean()
        self._errors.pop('username', None)
        return self.get_user() is not None

    def str_errors(self):
        return self._errors.get('__all__', '')


class CustomLoginView(LoginView):
    def form_valid(self, form):
        auth_login(self.request, form.get_user())
        return HttpResponseRedirect(self.get_success_url())

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/login', 'title': 'Авторизация'},
            ]),
            'signup_url': reverse('signup'),
            'password_reset_url': reverse('password_reset'),
            'feedback_url': reverse('feedback'),
        })
        return context

    def get_redirect_url(self):
        return reverse('main')


def login(request):
    return CustomLoginView.as_view(
        template_name='pages/login.html',
        redirect_authenticated_user=True,
        form_class=CustomAuthentificationForm,
    )(request)
