from constance import config
from smtplib import SMTPException

from django.conf import settings
from django.core.exceptions import ValidationError
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.core.validators import validate_email


def system_send_emails_to_recipients(list_of_recipients, html_message_pattern, subject):
    connection = EmailBackend(
        host=settings.EMAIL_HOST,
        port=settings.EMAIL_PORT,
        username=settings.EMAIL_HOST_USER,
        password=settings.EMAIL_HOST_PASSWORD,
    )
    mail = EmailMultiAlternatives(
        subject=subject,
        from_email='{} <{}>'.format(config.ADMIN_EMAILS_FROMNAME, settings.EMAIL_HOST_USER),
        to=list_of_recipients,
        connection=connection,
    )
    mail.attach_alternative(html_message_pattern, "text/html")

    try:
        connection.open()
        mail.send()
    except SMTPException:
        pass
    finally:
        connection.close()


def system_send_emails_to_admins(html_message_pattern, subject):
    list_of_admin_emails = []
    for email in config.ADMIN_EMAILS_LIST.split(';'):
        try:
            validate_email(email.strip())
            list_of_admin_emails.append(email.strip())
        except ValidationError:
            pass
    if list_of_admin_emails:
        system_send_emails_to_recipients(list_of_admin_emails, html_message_pattern, subject)


def client_send_email_to_recipient(client_email, html_message_pattern, subject, host, port, username, password):
    error = None

    try:
        connection = EmailBackend(
            host=host,
            port=port,
            username=username,
            password=password,
            use_tls=(port==587),
        )
        mail = EmailMultiAlternatives(
            subject=subject,
            from_email='{} <{}>'.format(config.ADMIN_EMAILS_FROMNAME, username),
            to=[client_email],
            connection=connection,
        )
        mail.attach_alternative(html_message_pattern, "text/html")

        try:
            connection.open()
            mail.send()
        except SMTPException as exc:
            error = '{}: {}'.format(exc.__class__.__name__, str(exc))
        finally:
            connection.close()
    except Exception as e:
        error = '{}: {}'.format(e.__class__.__name__, str(e))
    return error
