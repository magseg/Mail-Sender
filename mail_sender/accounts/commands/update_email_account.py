from core.commands import Command
from core.mixins import UserExistsValidatorMixin

from smtp.models import CustomSMTPServer, CommonSMTPServer
from smtp.commands import ValidateSMTPMixin
from .preupdate_validators import PreupdateEmailAccountValidatorMixin


class UpdateEmailAccount(UserExistsValidatorMixin, PreupdateEmailAccountValidatorMixin, ValidateSMTPMixin, Command):
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
        self.errors = []
        self.updated = False
        self.common_smtp = None
        self.custom_smtp = None

    def validate(self):
        self.validate_user_exists()
        self.validate_email_account_exists()
        self.validate_params()
        self.validate_host()
        self.validate_new_password()

    def execute_validated(self):
        if not self.errors:
            self.current_smtp_host = self.email_account.get_smtp_host()
            self.current_smtp_port = self.email_account.get_smtp_port()
            # Smtp
            if self.smtp_host != self.current_smtp_host or self.smtp_port != self.current_smtp_port:
                try:
                    self.common_smtp = CommonSMTPServer.objects.get(host=self.smtp_host, port=self.smtp_port)
                    self.smtp_name = self.common_smtp.name
                except CommonSMTPServer.DoesNotExist:
                    try:
                        self.custom_smtp = CustomSMTPServer.objects.get(
                            host=self.smtp_host, port=self.smtp_port, profile=self.user.profile)
                        self.smtp_name = self.custom_smtp.name
                    except CustomSMTPServer.DoesNotExist:
                        self.custom_smtp = CustomSMTPServer.objects.create(
                            profile=self.user.profile,
                            name=self.smtp_name,
                            host=self.smtp_host,
                            port=self.smtp_port,
                        )
                # Update
                self.email_account.custom_smtp = self.custom_smtp
                self.email_account.common_smtp = self.common_smtp
                self.updated = True
            if self.email_account.get_password() != self.new_password:
                self.updated = True
            # Update
            if self.updated:
                self.email_account.set_password(self.new_password)
                self.email_account.save()
                self.email_account.refresh_from_db()
        return self.updated, self.email_account, self.errors
