from django.contrib.auth.models import User


class UserExistsValidatorMixin(object):
    def __init__(self):
        self.user_id = None
        self.user = None
        self.profile = None
        self.errors = []

    def validate_user_exists(self):
        try:
            self.user = User.objects.get(id=self.user_id)
            self.profile = self.user.profile
            assert self.user.is_active
        except User.DoesNotExist:
            self.errors.append("Пользователя с указанным id не существует.")
        except (AttributeError, AssertionError):
            self.errors.append("Пользователь не активен.")
