from core.commands import Command
from core.mixins import UserExistsValidatorMixin

from ..models import Addressee, AddresseeList


class DeleteAddresseeLists(UserExistsValidatorMixin, Command):
    def __init__(self, user_id, addressee_lists_ids):
        self.user_id = user_id
        self.user = None
        self.errors = []
        self.addressee_lists_ids = addressee_lists_ids

    def validate(self):
        self.validate_user_exists()
        self.validate_addressee_lists_ids()
        self.validate_addressee_lists_db_integrity()

    def execute_validated(self):
        count = 0
        if not self.errors:
            count = AddresseeList.objects.filter(id__in=self.addressee_lists_ids).count()
            AddresseeList.objects.filter(id__in=self.addressee_lists_ids).update(is_published=False)
        return count, self.errors

    def validate_addressee_lists_ids(self):
        self.addressee_lists_ids = list(set(self.addressee_lists_ids))
        try:
            self.addressee_lists_ids = [int(d) for d in self.addressee_lists_ids]
        except ValueError:
            self.errors.append('Id должны быть в числовом формате.')
        try:
            assert len(self.addressee_lists_ids) > 0
        except AssertionError:
            self.errors.append('Передан пустой список id.')

    def validate_addressee_lists_db_integrity(self):
        new_ids = AddresseeList.objects.filter(id__in=self.addressee_lists_ids).values_list('id', flat=True)
        if len(new_ids) < len(self.addressee_lists_ids):
            self.errors.append(
                'Переданы id списков рассылки, которые отсутствуют в БД: {}'.format(
                    ''.join([str(d) for d in self.addressee_lists_ids if d not in new_ids]),
                )
            )
