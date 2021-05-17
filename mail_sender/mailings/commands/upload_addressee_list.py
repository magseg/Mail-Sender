from django.core.exceptions import ValidationError
from django.core.validators import validate_email

from core.commands import Command
from core.mixins import UserExistsValidatorMixin

from ..models import AddresseeList, Addressee


class UploadAddresseeList(UserExistsValidatorMixin, Command):
    def __init__(self, user_id, in_memory_uploaded_file):
        self.user_id = user_id
        self.user = None
        self.file = in_memory_uploaded_file
        self.filename = None
        self.decoded = None
        self.email_list = None
        self.valid_emails = []
        self.invalid_emails = []
        self.errors = []
        self.addressee_list = None

    def validate(self):
        self.validate_user_exists()
        self.decode_file()
        self.validate_emails()

    def execute_validated(self):
        if not self.errors:
            self.create_addressees()
        return (0, self.errors) if self.errors else (len(self.valid_emails), [])

    def decode_file(self):
        try:
            self.decoded = self.file.read().decode('utf-8')
        except UnicodeDecodeError:
            self.errors.append('Файл содержит недопустимые символы или отформатирован не в UTF-8. Переформатируйте файл в UTF-8.')
        except Exception as exc:
            self.errors.append('Ошибка чтения файла: {}. Обратитесь за помощью к системному администратору'.format(str(exc)))

    def validate_emails(self):
        if self.errors:
            return
        for n_email in self.decoded.splitlines():
            email = n_email.strip()
            if email == '':
                continue
            try:
                validate_email(email)
                if email not in self.valid_emails:
                    self.valid_emails.append(email)
            except ValidationError:
                self.invalid_emails.append(email)
        if not self.valid_emails:
            self.errors.append('Нет валидных email в файле.')
        if self.invalid_emails:
            self.errors.append('Невалидные email: ' + ', '.join(self.invalid_emails) + '.')

    def create_addressees(self):
        self.addressee_list = AddresseeList.objects.create(
            name=self.file.name,
            profile=self.user.profile,
        )
        addressee_list = []
        for email in self.valid_emails:
            addressee_list.append(Addressee(
                email=email,
                addressee_list=self.addressee_list,
            ))
        Addressee.objects.bulk_create(addressee_list)
