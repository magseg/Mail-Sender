from ..models import EmailAccount


class PreupdateEmailAccountValidatorMixin(object):
    def __init__(self):
        self.user_id = None
        self.user = None
        self.email_account_id = None
        self.smtp_host = None
        self.smtp_port = None
        self.smtp_name = None
        self.new_password = None
        self.email_account = None
        self.current_smtp_host = None
        self.current_smtp_port = None
        self.is_new_smtp = False
        self.is_common_smtp = False
        self.is_new_custom_smtp = False
        self.errors = []

    def validate_email_account_exists(self):
        try:
            self.email_account = EmailAccount.objects.get(id=self.email_account_id)
        except EmailAccount.DoesNotExist:
            self.errors.append('Email-аккаунт с указанным id не найден.')

    def validate_new_password(self):
        if not bool(self.new_password):
            self.errors.append('Новый пароль не может быть пустым.')
