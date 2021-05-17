# Generated by Django 2.2.5 on 2019-11-03 14:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailings', '0007_unsubscribe_reason'),
    ]

    operations = [
        migrations.AddField(
            model_name='senderhistory',
            name='from_name',
            field=models.TextField(blank=True, default='', verbose_name='Имя отправителя'),
        ),
        migrations.AddField(
            model_name='senderhistory',
            name='subject',
            field=models.TextField(blank=True, default='', verbose_name='Тема письма'),
        ),
    ]
