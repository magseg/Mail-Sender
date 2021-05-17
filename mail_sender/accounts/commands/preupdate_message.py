from django.template.loader import render_to_string

from core.commands import Command
from core.mixins import UserExistsValidatorMixin
from smtp.commands import ValidateSMTPMixin

from smtp.models import CustomSMTPServer, CommonSMTPServer
from .preupdate_validators import PreupdateEmailAccountValidatorMixin


class GetPreupdateMessage(UserExistsValidatorMixin, ValidateSMTPMixin, PreupdateEmailAccountValidatorMixin, Command):
    def __init__(self, user_id, email_account_id, new_smtp_host, new_smtp_port, new_password):
        self.user_id = int(user_id)
        self.user = None
        self.email_account_id = int(email_account_id)
        self.smtp_host = str(new_smtp_host)
        self.smtp_port = int(new_smtp_port)
        self.smtp_name = self.smtp_host
        self.new_password = str(new_password).strip()
        self.email_account = None
        self.current_smtp_host = None
        self.current_smtp_port = None
        self.is_new_smtp = False
        self.is_common_smtp = False
        self.is_new_custom_smtp = False
        self.is_new_password = False
        self.needs_update = False
        self.errors = []

    def validate(self):
        self.validate_user_exists()
        self.validate_email_account_exists()
        self.validate_params()
        self.validate_host()
        self.validate_new_password()

    def execute_validated(self):
        if not self.errors:
            self.check_if_new_smtp()
            self.check_if_new_password()
            self.needs_update = self.is_new_smtp or self.is_new_password

        return (
            bool(len(self.errors)),
            self.needs_update,
            render_to_string('email_accounts/preupdate_message.html', context={
                'smtp_name': self.smtp_name,
                'smtp_port': self.smtp_port,
                'smtp_host': self.smtp_host,
                'is_new_smtp': self.is_new_smtp,
                'is_new_custom_smtp': self.is_new_custom_smtp,
                'is_common_smtp': self.is_common_smtp,
                'errors': self.errors,
                'is_new_password': self.is_new_password,
                'needs_update': self.needs_update,
            }),
        )

    def check_if_new_smtp(self):
        self.current_smtp_host = self.email_account.get_smtp_host()
        self.current_smtp_port = self.email_account.get_smtp_port()
        if self.smtp_host != self.current_smtp_host or self.smtp_port != self.current_smtp_port:
            self.is_new_smtp = True
            try:
                common_smtp = CommonSMTPServer.objects.get(host=self.smtp_host, port=self.smtp_port)
                self.smtp_name = common_smtp.name
                self.is_common_smtp = True
            except CommonSMTPServer.DoesNotExist:
                try:
                    custom_smtp = CustomSMTPServer.objects.get(
                        host=self.smtp_host, port=self.smtp_port, profile=self.user.profile)
                    self.smtp_name = custom_smtp.name
                except CustomSMTPServer.DoesNotExist:
                    self.is_new_custom_smtp = True

    def check_if_new_password(self):
        old_password = self.email_account.get_password()
        if self.new_password != old_password:
            self.is_new_password = True
