from celery import shared_task

from .email_sender import EmailSenderWithHistory


@shared_task(bind=True, time_limit=86400*20, soft_time_limit=86400*10, acks_late=True)
def create_mailing(self, *args, **kwargs):
    mail_sender_obj = EmailSenderWithHistory(
        kwargs.get('history_id'),
        kwargs.get('recipients_list'),
        kwargs.get('host'),
        kwargs.get('port'),
        kwargs.get('username'),
        kwargs.get('password'),
        kwargs.get('html_message_pattern'),
        kwargs.get('subject'),
        kwargs.get('user_profile_id'),
        kwargs.get('html_template_id'),
        kwargs.get('email_account_id'),
        kwargs.get('fromname'),
        kwargs.get('cooldown'),
    )
    
    mail_sender_obj.init_mailing()
    del mail_sender_obj
