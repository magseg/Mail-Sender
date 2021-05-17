import string

from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.models import User
from django.contrib.auth.password_validation import validate_password

from core.commands import Command


class ChangeUserPassword(Command):
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

    def validate_user_exists(self):
        try:
            self.user = User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            self.errors.append("Пользователя с указанным id не существует.")

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


class ChangeUserInfo(Command):
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

    def validate_user_exists(self):
        try:
            self.user = User.objects.get(id=self.user_id)
        except User.DoesNotExist:
            self.errors.append("Пользователя с указанным id не существует.")

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
