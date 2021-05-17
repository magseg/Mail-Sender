from core.commands import Command
from core.mixins import UserExistsValidatorMixin
from smtp.models import CustomSMTPServer

from .mixins import ValidateSMTPMixin


class CreateCustomSMTP(UserExistsValidatorMixin, ValidateSMTPMixin, Command):
    def __init__(self, user_id, smtp_host, smtp_port, smtp_name=''):
        self.user_id = user_id
        self.user = None
        self.smtp_host = smtp_host
        self.smtp_port = smtp_port
        self.smtp_name = smtp_name or smtp_host
        self.errors = []
        self.custom_smtp = None

    def validate(self):
        self.validate_user_exists()
        self.validate_params()
        self.validate_host()

    def execute_validated(self):
        if not self.errors:
            self.custom_smtp, created = CustomSMTPServer.objects.get_or_create(
                profile=self.user.profile,
                host=self.smtp_host,
                port=self.smtp_port,
            )
            if created:
                self.custom_smtp.name = self.smtp_name
                self.custom_smtp.save()
            return self.custom_smtp, self.errors
        return None, self.errors
