import uuid

from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.authentication import TokenAuthentication
from rest_framework.exceptions import AuthenticationFailed

from accounts.models import EmailAccount


def get_authorization_header(request):
    auth = request.META.get('HTTP_API_KEY', b'')
    if isinstance(auth, str):
        auth = auth.encode(HTTP_HEADER_ENCODING)
    return auth


class WrongHeader(AuthenticationFailed):
    default_detail = 'Токен аутентификации имеет неверный формат.'


class WrongAccessToken(AuthenticationFailed):
    default_detail = 'Неверный токен авторизации.'


class AccessTokenAuthentication(TokenAuthentication):
    def authenticate(self, request):
        auth = get_authorization_header(request)
        try:
            token = auth.decode()
            token = str(uuid.UUID(token)).replace('-', '')
        except (UnicodeError, ValueError, TypeError):
            raise AuthenticationFailed(WrongHeader())
        return self.authenticate_credentials(token)

    def authenticate_credentials(self, token):
        email_account = EmailAccount.objects.filter(external_api_key=token).first()
        if email_account is None:
            raise AuthenticationFailed(WrongAccessToken())
        return email_account.profile.user, email_account
