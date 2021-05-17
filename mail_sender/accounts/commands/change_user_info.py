from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import User

from core.commands import Command
from core.mixins import UserExistsValidatorMixin


class ChangeUserInfo(UserExistsValidatorMixin, Command):
    def __init__(self, user_id, first_name, last_name, email):
        self.user_id = user_id
        self.user = None
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.errors = []

    def validate(self):
        self.validate_user_exists()
        self.validate_length()
        self.validate_email()
        if self.user:
            self.validate_email_is_unique()

    def execute_validated(self):
        if self.user and not self.errors:
            self.update_user_info()

    def validate_length(self):
        if len(self.first_name) > 254:
            self.errors.append("Максимальная длина поля Имя: 254 символа")
        if len(self.last_name) > 254:
            self.errors.append("Максимальная длина поля Фамилия: 254 символа")
        if len(self.email) > 254:
            self.errors.append("Максимальная длина поля Email: 254 символа")

    def validate_email(self):
        try:
            validate_email(self.email)
        except ValidationError:
            self.errors.append('Поле Email в неверном формате.')

    def validate_email_is_unique(self):
        if User.objects.filter(email=self.email).exclude(id=self.user_id).exists():
            self.errors.append('Этот Email уже используется.')

    def update_user_info(self):
        self.user.email = self.email
        self.user.first_name = self.first_name
        self.user.last_name = self.last_name
        self.user.save()
