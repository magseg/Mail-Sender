from core.commands import Command
from core.mixins import UserExistsValidatorMixin

from ..models import HTMLTemplate


class DeleteHTMLTemplates(UserExistsValidatorMixin, Command):
    def __init__(self, user_id, html_templates_ids):
        self.user_id = user_id
        self.user = None
        self.errors = []
        self.html_templates_ids = html_templates_ids

    def validate(self):
        self.validate_user_exists()
        self.validate_html_templates_ids()
        self.validate_html_templates_ids_db_integrity()

    def execute_validated(self):
        if not self.errors:
            count = HTMLTemplate.objects.filter(id__in=self.html_templates_ids).count()
            HTMLTemplate.objects.filter(id__in=self.html_templates_ids).update(is_published=False)
            return count, self.errors
        return 0, self.errors

    def validate_html_templates_ids(self):
        self.html_templates_ids = list(set(self.html_templates_ids))
        try:
            self.html_templates_ids = [int(d) for d in self.html_templates_ids]
        except ValueError:
            self.errors.append('Id должны быть в числовом формате.')
        try:
            assert len(self.html_templates_ids) > 0
        except AssertionError:
            self.errors.append('Передан пустой список id.')

    def validate_html_templates_ids_db_integrity(self):
        new_ids = HTMLTemplate.objects.filter(id__in=self.html_templates_ids).values_list('id', flat=True)
        if len(new_ids) < len(self.html_templates_ids):
            self.errors.append(
                'Переданы id шаблонов, которые отсутствуют в БД: {}'.format(
                    ''.join([str(d) for d in self.html_templates_ids if d not in new_ids]),
                )
            )
