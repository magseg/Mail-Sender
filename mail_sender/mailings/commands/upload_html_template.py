from core.commands import Command
from core.mixins import UserExistsValidatorMixin

from ..models import HTMLTemplate


class UploadHTMLTemplate(UserExistsValidatorMixin, Command):
    def __init__(self, user_id, in_memory_uploaded_file):
        self.user_id = user_id
        self.user = None
        self.file = in_memory_uploaded_file
        self.errors = []
        self.decoded = None

    def validate(self):
        self.validate_user_exists()
        self.decode_file()

    def execute_validated(self):
        if not self.errors:
            HTMLTemplate.objects.create(
                profile=self.user.profile,
                name=self.file.name,
                template=self.decoded,
            )
            return 1, []
        return 0, self.errors

    def decode_file(self):
        try:
            self.decoded = self.file.read().decode()
        except UnicodeDecodeError:
            self.errors.append('Файл содержит недопустимые символы. Отформатируйте его в UTF-8. Если это не помогло, обратитесь за помощью к системному администратору.')
        except Exception as exc:
            self.errors.append('Ошибка чтения файла: {}. Обратитесь за помощью к системному администратору'.format(str(exc)))
