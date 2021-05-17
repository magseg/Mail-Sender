from core.commands import Command
from core.mixins import UserExistsValidatorMixin

from .preupdate_validators import PreupdateEmailAccountValidatorMixin


class DeleteEmailAccount(UserExistsValidatorMixin, PreupdateEmailAccountValidatorMixin, Command):
    def __init__(self, user_id, email_account_id):
        self.user_id = user_id
        self.user = None
        self.email_account_id = email_account_id
        self.email_account = None
        self.errors = []

    def validate(self):
        self.validate_user_exists()
        self.validate_email_account_exists()

    def execute_validated(self):
        if not self.errors:
            self.email_account.is_published=False
            self.email_account.save()
        return self.errors
