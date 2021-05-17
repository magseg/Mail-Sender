import arrow
import logging
import time

from pymongo import MongoClient
from pymongo.errors import PyMongoError
from smtplib import SMTPException
from timeit import default_timer as timer

from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.core.mail.backends.smtp import EmailBackend
from django.urls import reverse

from core.email_sender import system_send_emails_to_admins
from .models import SenderHistory, HTMLTemplate


logger = logging.getLogger('main')


class EmailSenderWithHistory(object):
    def __init__(
        self, sender_history_id, recipients_list, host, port, username, password, html_message_pattern, subject,
        user_profile_id, html_template_id, email_account_id, fromname, cooldown,
    ):
        self.recipients_list = recipients_list
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.html_message_pattern = html_message_pattern
        self.subject = subject
        self.fromname = fromname
        self.cooldown = cooldown
        self.smtp_connection = None
        self.smtp_is_connected = False
        self.smtp_connection_error = None
        self.smtp_reconnection_attempts = 3
        self.mongo_connection_attempts = 3
        self.send_mail_attempts = 3
        self.sleep_between_reconnect = 0.1
        self.sender_history = None
        self.mongo_client = None
        self.mongo_is_connected = False
        self.mongo_db = None
        self.mongo_collection = None
        self.user_profile_id = user_profile_id
        self.mongo_connection_error_message = None
        self.email_account_id = email_account_id
        self.html_template_id = html_template_id
        self.total_sent = 0
        self.total_error = 0
        self.sender_history_id = sender_history_id

    def init_mailing(self):
        self.prepare_html_template()
        self.init_sender_history()
        self.init_mongo()
        if not self.mongo_is_connected:
            self.total_error = len(self.recipients_list)
            self.total_sent = 0
            self.finalize_sender_history()
            system_send_emails_to_admins(self.mongo_connection_error_message, 'Ошибка подключения к MongoDB')
            return
        self.reconnect()
        for recipient in self.recipients_list:
            self.send_mail(recipient)
        self.close()
        self.finalize_sender_history()

    def prepare_html_template(self):
        if self.html_template_id:
            return
        html_template = HTMLTemplate.objects.create(
            template=self.html_message_pattern,
            name='HTML-шаблон от {}'.format(str(arrow.utcnow().to(settings.FRONTEND_TIME_ZONE).datetime)[:19]),
        )
        self.html_template_id = html_template.id

    def init_sender_history(self):
        self.sender_history = SenderHistory.objects.get(id=self.sender_history_id)

        if self.user_profile_id:
            self.sender_history.profile_id = self.user_profile_id
        if self.email_account_id:
            self.sender_history.email_account_id = self.email_account_id
        if self.html_template_id:
            self.sender_history.html_template_id = self.html_template_id
        self.sender_history.save()

        self.mongo_connection_error_message = 'Ошибка подключения к MongoDb при <a href="{}">рассылке</a> ' \
                                              'на сайте <a href="{}">{}</a>'.format(
            settings.HTTP_DOMAIN + reverse('admin:{}_{}_change'.format(
                SenderHistory._meta.app_label,
                SenderHistory._meta.model_name
            ), args=(self.sender_history.id,)),
            settings.HTTP_DOMAIN,
            settings.HTTP_DOMAIN,
        )

    def finalize_sender_history(self):
        self.sender_history.successed += self.total_sent
        self.sender_history.failed += self.total_error
        self.sender_history.is_finalised = (self.sender_history.successed + self.sender_history.failed) == self.sender_history.total_mailings
        self.sender_history.save()
        self.mongo_client.close()

    def init_mongo(self):
        while self.mongo_connection_attempts and not self.mongo_is_connected:
            try:
                self.mongo_client = MongoClient(settings.MONGO_DB_HOST, settings.MONGO_DB_PORT, connect=True)
                self.mongo_db = self.mongo_client.mail_sender_2
                self.mongo_collection = self.mongo_db.history_items
                self.mongo_is_connected = True
            except PyMongoError:
                time.sleep(5)
                self.mongo_connection_attempts -= 1
                continue

    def connect(self):
        self.close()
        logger.debug('connecting')
        use_tls = (self.port == 587)
        use_ssl = (self.port == 465)
        self.smtp_connection = EmailBackend(
            host=self.host, port=self.port, username=self.username, password=self.password, use_tls=use_tls,
            use_ssl=use_ssl,
        )
        try:
            self.smtp_connection.open()
            self.smtp_is_connected = True
            self.smtp_connection_error = None
        except SMTPException as exc:
            self.smtp_connection_error = exc

    def close(self):
        self.smtp_is_connected = False
        if self.smtp_connection is None:
            return
        try:
            self.smtp_connection.close()
            self.smtp_connection = None
        except Exception:
            pass

    def insert_mongo_entry(self, recipient, error):
        self.mongo_collection.insert({
            'created_at': arrow.utcnow().datetime,
            'from': self.username,
            'to': recipient,
            'error': error,
            'sent': not error,
            'sender_history_id': self.sender_history.id,
        })

    def send_mail(self, recipient):
        mail = EmailMultiAlternatives(
            subject=self.subject,
            from_email='{} <{}>'.format(self.fromname, self.username),
            to=[recipient],
            connection=self.smtp_connection,
        )
        mail.attach_alternative(self.html_message_pattern, "text/html")
        end = 1.0
        start = 0.0
        error = ''
        mail_is_sent = False
        send_mail_attempts = self.send_mail_attempts

        while send_mail_attempts and not mail_is_sent:
            try:
                start = timer()
                mail.send()
                self.total_sent += 1
                mail_is_sent = True
                end = timer()
            except SMTPException as exc:
                error = '{}: {}'.format(exc.__class__.__name__, str(exc))
                self.reconnect()
            except Exception as exc:
                error = '{}: {}'.format(exc.__class__.__name__, str(exc))
            finally:
                send_mail_attempts -= 1
                if bool(error) and error.find('spam') > -1:
                    send_mail_attempts = 0

        if bool(error) or not mail_is_sent:
            self.total_error += 1

        if error and self.smtp_connection_error:
            error = '{}\n{}: {}'.format(
                error,
                self.smtp_connection_error.__class__,
                str(self.smtp_connection_error),
            )

        if error:
            logger.debug('{}, {}, {}'.format(self.username, recipient, error))

        self.insert_mongo_entry(recipient, error)

        if end - start < self.cooldown and end > start:
            time.sleep(round((self.cooldown - end + start) * 20.0 + 1.0) / 20.0)
        elif end < start:
            time.sleep(self.cooldown)

    def reconnect(self):
        connection_attempts = self.smtp_reconnection_attempts
        self.connect()
        connection_attempts -= 1
        while not self.smtp_is_connected and connection_attempts:
            time.sleep(self.sleep_between_reconnect)
            self.connect()
            connection_attempts -= 1
        return self.smtp_is_connected
