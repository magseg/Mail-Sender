# Generated by Django 2.2.5 on 2019-09-30 08:07

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0002_email_account_model'),
        ('smtp', '0003_fix_models'),
    ]

    operations = [
        migrations.AddField(
            model_name='customsmtpserver',
            name='profile',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='accounts.Profile', verbose_name='профиль'),
        ),
    ]
