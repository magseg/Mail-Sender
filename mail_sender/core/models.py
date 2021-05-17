from django.db import models


class PublishModel(models.Model):
    is_published = models.BooleanField(verbose_name='публикация', default=True)

    class Meta:
        abstract = True

    def publish(self):
        self.is_published = True
        super(PublishModel, self).save()

    def unpublish(self):
        self.is_published = False
        super(PublishModel, self).save()


class FAQ(PublishModel):
    question = models.TextField(verbose_name='вопрос', default='', blank=True)
    answer = models.TextField(verbose_name='ответ', default='', blank=True)

    def __str__(self):
        return self.question

    class Meta:
        verbose_name = 'Часто задаваемый вопрос'
        verbose_name_plural = 'Часто задаваемые вопросы'


class ClientQuestion(models.Model):
    created_at = models.DateTimeField(verbose_name='дата создания', auto_now_add=True)
    profile = models.ForeignKey('accounts.Profile', verbose_name='профиль', on_delete=models.PROTECT)
    question = models.TextField(verbose_name='вопрос', default='', blank=True)
    answer = models.TextField(verbose_name='ответ', default='', blank=True)

    def __str__(self):
        return 'Вопрос пользователя {} от {}'.format(self.profile, self.created_at)

    class Meta:
        verbose_name = 'Вопрос клиента'
        verbose_name_plural = 'Вопросы клиентов'


class Feedback(models.Model):
    created_at = models.DateTimeField(verbose_name='дата создания', auto_now_add=True)
    profile = models.ForeignKey('accounts.Profile', verbose_name='профиль', on_delete=models.PROTECT,
                                null=True, blank=True)
    email = models.EmailField(verbose_name='email', max_length=255, blank=True, default='')
    name = models.CharField(verbose_name='имя', max_length=255, blank=True, default='')
    feedback_text = models.TextField(verbose_name='текст обращения', blank=True, default='')

    def __str__(self):
        return 'Обращение {} от {}'.format(self.name, self.created_at.isoformat())

    class Meta:
        verbose_name = 'Обратная связь'
        verbose_name_plural = 'Обратная связь'
