from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from core.models import PublishModel
from smtp.models import CommonSMTPServer, CustomSMTPServer

from core.utils import cipher_password, decipher_password, get_uuid_string

from .managers import EmailAccountManager


class Profile(PublishModel):
    user = models.OneToOneField(User, verbose_name='Django-пользователь', on_delete=models.PROTECT)
    is_confirmed = models.BooleanField(verbose_name='подтвержденный аккаунт', default=False)
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Дата добавления')

    class Meta:
        verbose_name = 'Профиль пользователя'
        verbose_name_plural = 'Профили пользователей'

    def __str__(self):
        if self.user.last_name or self.user.first_name:
            return '{} {}'.format(self.user.last_name, self.user.first_name)
        return self.user.username

    def save(self, *args, **kwargs):
        self.user.is_active = self.is_confirmed
        self.user.save()
        super().save(*args, **kwargs)


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(
            user=instance,
            is_confirmed=instance.is_staff,
        )


class EmailAccount(PublishModel):
    profile = models.ForeignKey(Profile, verbose_name='Профиль', on_delete=models.PROTECT,
                                related_name='email_accounts')
    email = models.EmailField(verbose_name='Email', max_length=255, default='', blank=True)
    password = models.CharField(verbose_name='Пароль', max_length=255, default='', blank=True)
    common_smtp = models.ForeignKey(CommonSMTPServer, verbose_name='общий smtp',
                                    blank=True, null=True, on_delete=models.PROTECT)
    custom_smtp = models.ForeignKey(CustomSMTPServer, verbose_name='пользовательский smtp',
                                    blank=True, null=True, on_delete=models.PROTECT)
    unsubscribed_key = models.CharField(verbose_name='ключ для отписки', max_length=254,
                                        default=get_uuid_string, blank=True)
    external_api_key = models.CharField(verbose_name='ключ для внешнего API', max_length=254,
                                        default=get_uuid_string, blank=True)

    objects = EmailAccountManager()

    class Meta:
        verbose_name = 'Email-аккаунт'
        verbose_name_plural = 'Email-аккаунты'

    def __str__(self):
        return 'Аккаунт {}'.format(self.email)

    def delete(self, *args, **kwargs):
        self.is_published = False
        super().save()

    def set_password(self, password):
        self.password = cipher_password(password)
        super().save()

    def get_password(self):
        return decipher_password(self.password) if self.password else None

    def get_smtp_host(self):
        if self.common_smtp:
            return self.common_smtp.host
        elif self.custom_smtp:
            return self.custom_smtp.host
        return None

    def get_smtp_port(self):
        if self.common_smtp:
            return self.common_smtp.port
        elif self.custom_smtp:
            return self.custom_smtp.port
        return None

    def get_cooldown(self):
        return 1
