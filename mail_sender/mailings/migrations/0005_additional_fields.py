# Generated by Django 2.2.5 on 2019-10-12 11:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mailings', '0004_sender_history_model'),
    ]

    operations = [
        migrations.AddField(
            model_name='senderhistory',
            name='failed',
            field=models.IntegerField(default=0, verbose_name='неудачных отправок'),
        ),
        migrations.AddField(
            model_name='senderhistory',
            name='is_finalised',
            field=models.BooleanField(default=False, verbose_name='отчет финализирован'),
        ),
        migrations.AddField(
            model_name='senderhistory',
            name='successed',
            field=models.IntegerField(default=0, verbose_name='удачных отправок'),
        ),
        migrations.AddField(
            model_name='senderhistory',
            name='total_mailings',
            field=models.IntegerField(default=0, verbose_name='общее число'),
        ),
    ]