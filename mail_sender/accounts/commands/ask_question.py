from django.conf import settings
from django.urls import reverse

from core.commands import Command
from core.mixins import UserExistsValidatorMixin
from core.models import ClientQuestion
from core.tasks import send_email_to_admin_async


class RegisterClientQuestion(UserExistsValidatorMixin, Command):
    def __init__(self, user_id, question):
        self.user_id = user_id
        self.user = None
        self.question = str(question).strip()
        self.client_question = None
        self.errors = []

    def validate(self):
        self.validate_user_exists()
        self.validate_question()

    def execute_validated(self):
        if not self.errors:
            self.create_question_object()
            self.send_mail_to_admin()
        return self.errors

    def validate_question(self):
        if len(self.question) == 0:
            self.errors.append('Поле вопроса не может быть пустым.')

    def create_question_object(self):
        self.client_question = ClientQuestion.objects.create(
            profile=self.user.profile,
            question=self.question,
        )

    def send_mail_to_admin(self):
        send_email_to_admin_async.apply_async(
            (
                'Пользователь {} задал <a href="{}">новый вопрос</a> на сайте <a href="{}">{}</a>'.format(
                    self.user.profile,
                    settings.HTTP_DOMAIN + reverse('admin:{}_{}_change'.format(
                        ClientQuestion._meta.app_label,
                        ClientQuestion._meta.model_name
                    ), args=(self.client_question.id,)),
                    settings.HTTP_DOMAIN,
                    settings.HTTP_DOMAIN,
                ),
                'Вопрос пользователя mail-sender',
            ),
        )
