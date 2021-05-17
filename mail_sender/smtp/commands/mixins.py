from django.core.exceptions import ValidationError
from django.core.validators import validate_ipv46_address

from core.validators import validate_domain_name


class ValidateSMTPMixin(object):
    def __init__(self):
        self.errors = []
        self.smtp_host = None
        self.smtp_port = None
        self.smtp_name = None

    def validate_host(self):
        try:
            validate_ipv46_address(self.smtp_host)
        except ValidationError:
            try:
                validate_domain_name(self.smtp_host)
            except ValidationError:
                self.errors.append('SMTP-сервер должен представлять корректный IPv4, или IPv6, или доменное имя.')

    def validate_params(self):
        try:
            self.smtp_port = int(self.smtp_port)
        except (ValueError, TypeError):
            self.errors.append('Порт должен иметь числовой формат.')

        try:
            assert type(self.smtp_host) == str
            assert type(self.smtp_name) == str
            assert len(self.smtp_name) < 255
        except AssertionError:
            self.errors.append('Параметр имеет некорректный формат.')