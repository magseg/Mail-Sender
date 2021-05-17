from django.db import models


class EmailAccountQuerySet(models.QuerySet):
    def delete(self, *args, **kwargs):
        super().update(is_published=False)


class EmailAccountManager(models.Manager):
    def get_queryset(self):
        return EmailAccountQuerySet(self.model, using=self._db)
