from celery import shared_task

from django.conf import settings

from .email_sender import system_send_emails_to_recipients, system_send_emails_to_admins


@shared_task(bind=True, time_limit=settings.CELERY_TASK_TIME_LIMIT, acks_late=True)
def send_email_to_admin_async(self, html_message_pattern, subject):
    system_send_emails_to_admins(html_message_pattern, subject)


@shared_task(bind=True, time_limit=settings.CELERY_TASK_TIME_LIMIT, acks_late=True)
def send_email_to_user_async(self, list_of_recipients, html_message_pattern, subject):
    system_send_emails_to_recipients(list_of_recipients, html_message_pattern, subject)
