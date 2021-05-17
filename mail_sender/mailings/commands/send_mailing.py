import time
from celery import chain
from smtplib import SMTPException

from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend

from accounts.models import EmailAccount
from core.commands import Command
from core.mixins import UserExistsValidatorMixin
from core.utils import clean_html

from ..models import HTMLTemplate, SenderHistory
from ..tasks import create_mailing


class SendMailing(UserExistsValidatorMixin, Command):
    def __init__(
        self,
        user_id,
        email_account_id,
        client_email_list,
        html_template_id,
        subject,
        fromname='',
        cooldown=0,
    ):
        self.user_id = user_id
        self.user = None
        self.email_account_id = email_account_id
        self.email_account = None
        self.addressee_list = None
        self.html_template_id = html_template_id
        self.html_template = None
        self.email_list = client_email_list
        self.smtp_host = None
        self.smtp_port = None
        self.subject = str(subject).strip()
        self.cooldown = cooldown
        self.total = 0
        self.success = 0
        self.failed = 0
        self.fromname = str(fromname)
        self.errors = []
        self.split_email_list_by = 10
        self.sender_history_obj = None

    def validate(self):
        self.validate_user_exists()
        self.validate_email_account()
        self.validate_params()
        self.validate_html_template()

    def execute_validated(self):
        if not self.errors:
            self.create_sender_history_obj()
            self.asynchronous_send()
            return [], self.sender_history_obj
        return self.errors, None

    ##############################################################################################################

    def create_sender_history_obj(self):
        self.sender_history_obj = SenderHistory.objects.create(
            total_mailings=len(self.email_list),
            from_name=self.fromname or self.email_account.email,
            subject=self.subject,
        )

    def validate_params(self):
        try:
            self.email_account_id = int(self.email_account_id)
        except (ValueError, TypeError):
            self.errors.append('Id email-аккаунта должен иметь числовой формат.')
        try:
            self.cooldown = int(self.cooldown) / 10.0
        except (ValueError, TypeError):
            self.errors.append('Поле "задержка между запросами" должно иметь числовой формат.')
        if len(self.subject) > 988:
            self.errors.append(
                'Максимальная длина поля "Тема сообщения", согласно стандарту RFC 2822, составляет 988 символов.'
            )
        if len(self.subject) == 0:
            self.errors.append(
                'Поле "Тема сообщения" не может быть пустым.'
            )
        if len(self.email_account.email) + len(self.fromname) + 3 > 250:
            self.errors.append(
                'Суммарная длина Email и имени отправителя не должна превышать 254 символа.'
            )

    def validate_email_account(self):
        self.email_account = EmailAccount.objects.filter(id=self.email_account_id).first()
        if self.email_account is None:
            self.errors.append('Email-аккаунт с указанным id не найден.')
            return
        self.smtp_host = self.email_account.get_smtp_host()
        self.smtp_port = self.email_account.get_smtp_port()
        try:
            assert bool(self.smtp_host)
            assert bool(self.smtp_port)
        except AssertionError:
            self.errors.append('Неправильно выставлен хост или порт для Email-аккаунта. '
                               'Проверьте настройки на странице аккаунта или обратитесь к системному администратору.')

    def validate_html_template(self):
        self.html_template = HTMLTemplate.objects.filter(id=self.html_template_id).first()
        if self.html_template is None:
            self.errors.append('HTML-шаблон с указанным id не найден.')
            return
        self.html_template = clean_html(self.html_template.template.strip())
        try:
            assert bool(self.html_template)
        except AssertionError:
            self.errors.append('HTML-шаблон пуст.')

    def validate_subject(self):
        self.subject = self.subject.replace(' ', chr(11))
        self.fromname = self.fromname.replace(' ', chr(11))

    def asynchronous_send(self):
        array_of_tasks = []
        t = len(self.email_list)
        for i in range(0, (t // self.split_email_list_by) + bool(t % self.split_email_list_by)):
            array_of_tasks.append(create_mailing.s((),
                history_id=self.sender_history_obj.id,
                recipients_list=self.email_list[i*self.split_email_list_by:(i+1)*self.split_email_list_by],
                host=self.smtp_host,
                port=self.smtp_port,
                username=self.email_account.email,
                password=self.email_account.get_password(),
                html_message_pattern=self.html_template,
                subject=self.subject,
                user_profile_id=self.user.profile.id,
                html_template_id=self.html_template_id,
                email_account_id=self.email_account_id,
                fromname=self.fromname,
                cooldown=self.cooldown,
            ))
        chain(*array_of_tasks).apply_async()

    def synchronous_send(self):
        with EmailBackend(
            host=self.smtp_host,
            port=self.smtp_port,
            username=self.email_account.email,
            password=self.email_account.get_password(),
        ) as connection:
            for email in self.email_list:
                try:
                    mail = EmailMultiAlternatives(
                        subject=self.subject,
                        from_email=self.email_account.email,
                        bcc=[email],
                        connection=connection,
                    )
                    mail.attach_alternative(self.html_template, "text/html")
                    mail.send()
                    time.sleep(self.cooldown)
                except SMTPException as exc:
                    self.errors.append('{} - ошибка отправки {}: {}'.format(email, exc.__class__.__name__, str(exc)))
