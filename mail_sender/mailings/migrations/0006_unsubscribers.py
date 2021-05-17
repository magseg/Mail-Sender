# Generated by Django 2.2.5 on 2019-10-18 14:34

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_add_external_keys'),
        ('mailings', '0005_additional_fields'),
    ]

    operations = [
        migrations.CreateModel(
            name='Unsubscriber',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='дата создания')),
                ('email', models.EmailField(blank=True, default='', max_length=254, verbose_name='email')),
                ('email_account', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.EmailAccount', verbose_name='email-аккаунт')),
            ],
            options={
                'verbose_name': 'Отписавшийся от аккаунта',
                'verbose_name_plural': 'Отписавшиеся от аккаунтов',
            },
        ),
    ]
