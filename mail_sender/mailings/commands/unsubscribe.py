from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from core.commands import Command

from accounts.models import EmailAccount
from ..models import Addressee, Unsubscriber


class Unsubscribe(Command):
    def __init__(self, email, email_account_id, reason):
        self.email_account_id = int(email_account_id)
        self.email = str(email).strip()
        self.email_account = None
        self.errors = []
        self.reason = reason

    def validate(self):
        self.validate_email_account_exists()
        self.validate_email()
        self.validate_is_not_yet_unsubscribed()

    def execute_validated(self):
        if not self.errors:
            Unsubscriber.objects.create(
                email_account=self.email_account,
                reason=self.reason,
                email=self.email,
            )
        return self.errors

    def validate_email_account_exists(self):
        try:
            self.email_account = EmailAccount.objects.get(id=self.email_account_id)
        except EmailAccount.DoesNotExist:
            self.errors.append('Email-аккаунт с указанным id не найден.')

    def validate_email(self):
        try:
            validate_email(self.email)
        except ValidationError:
            self.errors.append('Невалидный email.')

    def validate_is_not_yet_unsubscribed(self):
        if Unsubscriber.objects.filter(email_account=self.email_account, email=self.email).exists():
            self.errors.append('Этот email уже отписан от рассылки.')
