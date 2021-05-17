import string

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password

from core.commands import Command
from core.mixins import UserExistsValidatorMixin


class ChangeUserPassword(UserExistsValidatorMixin, Command):
    def __init__(self, user_id, old_password, new_password_1, new_password_2):
        self.user_id = user_id
        self.user = None
        self.old_password = old_password
        self.new_password_1 = new_password_1
        self.new_password_2 = new_password_2
        self.allowed_chars = string.digits + string.ascii_letters + string.punctuation
        self.errors = []

    def validate(self):
        self.validate_user_exists()
        self.validate_new_passwords_match()
        self.validate_password_symbols()
        self.django_validate_password()
        if self.user:
            self.validate_password()

    def execute_validated(self):
        if not self.errors and self.user:
            self.user.set_password(self.new_password_1)
            self.user.save()
        return self.errors

    def validate_password(self):
        if not self.user.check_password(self.old_password):
            self.errors.append("Неверный прежний пароль.")

    def validate_new_passwords_match(self):
        if self.new_password_1 != self.new_password_2:
            self.errors.append("Новые пароли не совпадают.")

    def validate_password_symbols(self):
        for char in self.new_password_1:
            if char not in self.allowed_chars:
                self.errors.append(
                    "Пароль содержит недопустимые символы. Допустимые символы: {}".format(self.allowed_chars),
                )

    def django_validate_password(self):
        try:
            validate_password(self.new_password_1)
        except ValidationError as errors:
            for error in errors:
                self.errors.append(error)
