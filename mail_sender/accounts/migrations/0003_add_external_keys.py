# Generated by Django 2.2.5 on 2019-10-10 15:11

import core.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_email_account_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='emailaccount',
            name='external_api_key',
            field=models.CharField(blank=True, default=core.utils.get_uuid_string, max_length=254, verbose_name='ключ для внешнего API'),
        ),
        migrations.AddField(
            model_name='emailaccount',
            name='unsubscribed_key',
            field=models.CharField(blank=True, default=core.utils.get_uuid_string, max_length=254, verbose_name='ключ для отписки'),
        ),
    ]