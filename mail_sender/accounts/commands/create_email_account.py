from core.commands import Command
from core.mixins import UserExistsValidatorMixin

from smtp.models import CommonSMTPServer, CustomSMTPServer
from ..models import EmailAccount


class CreateEmailAccount(UserExistsValidatorMixin, Command):
    def __init__(self, user_id, email, password, common_smtp_id=None, custom_smtp_id=None):
        self.user_id = user_id
        self.user = None
        self.email = email
        self.password = password
        self.common_smtp_id = common_smtp_id
        self.common_smtp = None
        self.custom_smtp_id = custom_smtp_id
        self.custom_smtp = None
        self.errors = []
        self.email_account = None

    def validate(self):
        self.validate_user_exists()
        if not self.errors:
            self.validate_one_smtp_provided()

    def execute_validated(self):
        if not self.errors:
            self.email_account = EmailAccount.objects.create(
                profile=self.user.profile,
                email=self.email,
                common_smtp=self.common_smtp,
                custom_smtp=self.custom_smtp,
            )
            self.email_account.refresh_from_db()
            self.email_account.set_password(self.password)
            return self.email_account, self.errors
        return None, self.errors

    def validate_one_smtp_provided(self):
        if not (bool(self.common_smtp_id) ^ bool(self.custom_smtp_id)):
            self.errors.append('Необходимо предоставить один id SMTP.')
        elif self.common_smtp_id:
            try:
                self.common_smtp = CommonSMTPServer.objects.get(id=self.common_smtp_id)
            except CommonSMTPServer.DoesNotExist:
                self.errors.append('Сервер SMTP с указанным id не найден.')
        else:
            try:
                self.custom_smtp = CustomSMTPServer.objects.get(id=self.custom_smtp_id, profile=self.user.profile)
            except CustomSMTPServer.DoesNotExist:
                self.errors.append('Пользовательский сервер SMTP с указанным id не найден.')
