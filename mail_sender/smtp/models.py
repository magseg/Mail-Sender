from django.db import models

from core.models import PublishModel


class CommonSMTPServer(PublishModel):
    name = models.CharField(verbose_name='название', default='', blank=True, max_length=255)
    host = models.CharField(verbose_name='сервер', default='', blank=True, max_length=255)
    port = models.IntegerField(verbose_name='порт', default=0)

    class Meta:
        verbose_name = 'Общий SMTP-сервер'
        verbose_name_plural = 'Общие SMTP-серверы'

    def __str__(self):
        return 'SMTP-сервер {}'.format(self.host)


class CustomSMTPServer(PublishModel):
    name = models.CharField(verbose_name='название', default='', blank=True, max_length=255)
    host = models.CharField(verbose_name='сервер', default='', blank=True, max_length=255)
    port = models.IntegerField(verbose_name='порт', default=0)
    profile = models.ForeignKey('accounts.Profile', verbose_name='профиль',
                                null=True, blank=True, on_delete=models.PROTECT)

    class Meta:
        verbose_name = 'Пользовательский SMTP-сервер'
        verbose_name_plural = 'Пользовательские SMTP-серверы'

    def __str__(self):
        return 'Пользовательский SMTP-сервер {}'.format(self.host)
