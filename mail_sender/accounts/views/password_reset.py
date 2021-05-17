from django import forms
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.shortcuts import render
from django.template import loader
from django.utils.decorators import decorator_from_middleware

from core.middlewares import IsAuthenticatedMiddleware
from core.tasks import send_email_to_user_async
from core.utils import generate_breadcumbs


class CustomPasswordResetForm(PasswordResetForm):

    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(attrs={'class': 'form-control', 'type': 'email'}),
    )

    def send_mail(
        self,
        subject_template_name,
        email_template_name,
        context,
        from_email,
        to_email,
        html_email_template_name=None,
    ):
        subject = loader.render_to_string(subject_template_name, context)
        subject = ''.join(subject.splitlines())
        message = loader.render_to_string(email_template_name, context)
        send_email_to_user_async.apply_async(([to_email], message, subject, ),)


class CustomSetPasswordForm(SetPasswordForm):

    new_password1 = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        strip=False,
    )

    new_password2 = forms.CharField(
        strip=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
    )


@decorator_from_middleware(IsAuthenticatedMiddleware)
def password_reset_api(request):
    return render(
        request,
        'pages/password_reset.html',
        context={
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/password_reset', 'title': 'Восстановление пароля'},
            ])
        }
    )


class PasswordResetViewContextMixin(object):
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/', 'title': 'Восстановление пароля'},
            ])
        })
        return context


class CustomPasswordResetView(PasswordResetViewContextMixin, auth_views.PasswordResetView):
    pass


class CustomPasswordResetDoneView(PasswordResetViewContextMixin, auth_views.PasswordResetDoneView):
    pass


class CustomPasswordResetConfirmView(PasswordResetViewContextMixin, auth_views.PasswordResetConfirmView):
    pass


class CustomPasswordResetCompleteView(PasswordResetViewContextMixin, auth_views.PasswordResetCompleteView):
    pass


def password_reset_view(request):
    return CustomPasswordResetView.as_view(
        email_template_name='accounts/password_reset_email.html',
        form_class=CustomPasswordResetForm,
        template_name='accounts/password_reset_form.html',
        subject_template_name='accounts/password_reset_subject.txt',
    )(request)


def password_reset_done_view(request):
    return CustomPasswordResetDoneView.as_view(
        template_name='accounts/password_reset_done.html'
    )(request)


def password_reset_confirm_view(request, uidb64='', token=''):
    return CustomPasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html',
        form_class=CustomSetPasswordForm,
    )(request, uidb64=uidb64, token=token)


def password_reset_complete_view(request):
    return CustomPasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html',
    )(request)
