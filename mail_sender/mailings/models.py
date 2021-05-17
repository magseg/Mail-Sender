import datetime

from django.db import models

from accounts.models import Profile, EmailAccount
from core.models import PublishModel


class HTMLTemplate(PublishModel):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='дата последнего обновления')
    profile = models.ForeignKey(Profile, verbose_name='профиль', on_delete=models.PROTECT,
                                related_name='html_templates', null=True, blank=True)
    template = models.TextField(verbose_name='html-шаблон', default='', blank=True)
    name = models.CharField(verbose_name='Название', default='', blank=True, max_length=254)

    def __str__(self):
        return 'HTML-шаблон {} пользователя {}'.format(self.name, self.profile)

    class Meta:
        verbose_name = 'HTML-шаблон'
        verbose_name_plural = 'HTML-шаблоны'


class AddresseeList(PublishModel):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    last_modified = models.DateTimeField(auto_now=True, verbose_name='дата последнего обновления')
    profile = models.ForeignKey(Profile, verbose_name='профиль',
                                on_delete=models.PROTECT, related_name='addressee_lists')
    name = models.CharField(verbose_name='Название', default='', blank=True, max_length=254)

    def __str__(self):
        return 'Список адресатов {} пользователя {}'.format(self.name, self.profile)

    class Meta:
        verbose_name = 'Список адресатов'
        verbose_name_plural = 'Списки адресатов'


class Addressee(models.Model):
    email = models.EmailField(verbose_name='email', max_length=254, default='', blank=True)
    addressee_list = models.ForeignKey(AddresseeList, verbose_name='список адресатов',
                                       related_name='addressees', on_delete=models.PROTECT)

    def __str__(self):
        return 'Адресат {}'.format(self.email)

    class Meta:
        verbose_name = 'Адресат'
        verbose_name_plural = 'Адресаты'
        unique_together = ('email', 'addressee_list', )


class SenderHistory(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    html_template = models.ForeignKey(HTMLTemplate, verbose_name='HTML-шаблон',
                                      on_delete=models.PROTECT, null=True, blank=True)
    profile = models.ForeignKey(Profile, verbose_name='профиль', on_delete=models.PROTECT, null=True, blank=True)
    email_account = models.ForeignKey(EmailAccount, verbose_name='email-аккаунт',
                                      on_delete=models.PROTECT, null=True, blank=True)
    total_mailings = models.IntegerField(verbose_name='общее число', default=0)
    successed = models.IntegerField(verbose_name='удачных отправок', default=0)
    failed = models.IntegerField(verbose_name='неудачных отправок', default=0)
    is_finalised = models.BooleanField(verbose_name='отчет финализирован', default=False)
    from_name = models.TextField(verbose_name='Имя отправителя', default='', blank=True)
    subject = models.TextField(verbose_name='Тема письма', default='', blank=True)

    def __str__(self):
        if self.email_account and self.email_account.email and isinstance(self.created_at, datetime.datetime):
            return 'Объект истории аккаунта {} от {}'.format(
                self.email_account.email,
                self.created_at.isoformat(),
            )
        elif self.email_account and self.email_account.email:
            return 'Объект истории аккаунта {}'.format(self.email_account.email)
        else:
            return 'Объект истории аккаунта {}'.format(self.id)

    class Meta:
        verbose_name = 'История рассылки'
        verbose_name_plural = 'История рассылки'


class Unsubscriber(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='дата создания')
    email_account = models.ForeignKey(EmailAccount, verbose_name='email-аккаунт',
                                      on_delete=models.PROTECT, null=True, blank=True)
    email = models.EmailField(verbose_name='email', max_length=254, default='', blank=True)
    reason = models.TextField(verbose_name='причина отписки', default='', blank=True)

    def __str__(self):
        return 'Отписавшийся {} от рассылки {}'.format(self.email, self.email_account)

    class Meta:
        verbose_name = 'Отписавшийся от аккаунта'
        verbose_name_plural = 'Отписавшиеся от аккаунтов'
