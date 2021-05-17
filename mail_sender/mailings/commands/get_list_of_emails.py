from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from core.commands import Command
from core.mixins import UserExistsValidatorMixin

from accounts.models import EmailAccount
from ..models import AddresseeList, Unsubscriber


class GetListOfEmails(UserExistsValidatorMixin, Command):
    def __init__(self, user_id, addressee_list_id, email_account_id, custom_addressee_list=None):
        self.user_id = user_id
        self.user = None
        self.errors = []
        self.addressee_list_id = addressee_list_id
        self.addressee_list = None
        self.email_list = []
        self.custom_addressee_list = custom_addressee_list
        self.email_account_id = email_account_id
        self.email_account = None

    def validate(self):
        self.validate_user_exists()
        self.validate_email_account()
        self.validate_addressee_list_exists()
        self.assert_email_list()

    def execute_validated(self):
        self.treat_unsubscribers()
        return self.email_list, self.errors

    def validate_email_account(self):
        try:
            self.email_account_id = int(self.email_account_id)
            self.email_account = EmailAccount.objects.filter(id=self.email_account_id).first()
            if self.email_account is None:
                self.errors.append('Email-аккаунт с указанным id не найден.')
        except (TypeError, ValueError):
            self.errors.append('Email-аккаунт с указанным id не найден.')

    def validate_addressee_list_exists(self):
        try:
            self.addressee_list_id = int(self.addressee_list_id)
            if self.addressee_list_id != 0:
                self.addressee_list = AddresseeList.objects.filter(
                    id=self.addressee_list_id,
                    profile=self.user.profile,
                ).first()
                if self.addressee_list is None:
                    self.errors.append('Списка рассылки с указанным id не существует.')
        except (TypeError, ValueError):
            self.errors.append('Id должен иметь числовой тип.')

    def assert_email_list(self):
        if self.addressee_list and self.addressee_list_id != 0:
            self.email_list = [d.email for d in self.addressee_list.addressees.all()]
        elif self.addressee_list_id == 0:
            try:
                assert bool(self.custom_addressee_list)
                assert type(self.custom_addressee_list) == str
            except AssertionError:
                self.errors.append('Пользовательский список рассылки имеет неверный тип.')
            email_list = self.custom_addressee_list.split(';')
            erroneous_emails = []
            for email in email_list:
                try:
                    validate_email(email.strip())
                    self.email_list.append(email.strip())
                except ValidationError:
                    erroneous_emails.append(email)
            if erroneous_emails:
                self.errors.append(
                    'Некоторые из введенных email имеют неправильный формат:\n{}.'.format(
                        '\n'.join(erroneous_emails)
                    )
                )
        else:
            self.errors.append('Должен быть передан id списка рассылки или указанный вручную список рассылки.')

    def treat_unsubscribers(self):
        if len(self.email_list) == 0:
            self.errors.append('Список рассылки пуст.')
        unsubscribers = set(
            Unsubscriber.objects.filter(email_account=self.email_account).values_list('email', flat=True)
        )
        self.email_list = [d for d in self.email_list if d not in unsubscribers]
        if len(self.email_list) == 0:
            self.errors.append('Все клиенты рассылки отписались от рассылки.')
