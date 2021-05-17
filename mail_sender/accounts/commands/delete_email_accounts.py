from core.commands import Command
from core.mixins import UserExistsValidatorMixin

from ..models import EmailAccount


class DeleteEmailAccounts(UserExistsValidatorMixin, Command):
    def __init__(self, user_id, email_account_ids):
        self.user_id = user_id
        self.user = None
        self.profile = None
        self.email_account_ids = email_account_ids
        self.errors = []

    def validate(self):
        self.validate_user_exists()
        self.validate_email_accounts_ids()
        if self.user:
            self.validate_email_account_ids_db_integrity()

    def execute_validated(self):
        if not self.errors:
            count = EmailAccount.objects.filter(id__in=self.email_account_ids).count()
            EmailAccount.objects.filter(id__in=self.email_account_ids).update(is_published=False)
            return count, self.errors
        return 0, self.errors

    def validate_email_accounts_ids(self):
        self.email_account_ids = list(set(self.email_account_ids))
        try:
            self.email_account_ids = [int(d) for d in self.email_account_ids]
        except ValueError:
            self.errors.append('Id должны быть в числовом формате.')
        try:
            assert len(self.email_account_ids) > 0
        except AssertionError:
            self.errors.append('Передан пустой список id.')

    def validate_email_account_ids_db_integrity(self):
        new_ids = EmailAccount.objects.filter(
            id__in=self.email_account_ids,
            is_published=True,
        ).values_list('id', flat=True)
        if len(new_ids) < len(self.email_account_ids):
            self.errors.append(
                'Переданы id аккаунтов, которые отсутствуют в БД: {}'.format(
                    ''.join([str(d) for d in self.email_account_ids if d not in new_ids]),
                )
            )
