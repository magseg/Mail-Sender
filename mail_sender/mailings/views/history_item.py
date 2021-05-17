from pymongo import MongoClient

from django.conf import settings
from django.http import Http404
from django.shortcuts import render
from django.utils.decorators import decorator_from_middleware
from django.urls import reverse

from core.middlewares import IsAuthenticatedMiddleware
from core.utils import generate_breadcumbs

from ..models import SenderHistory


@decorator_from_middleware(IsAuthenticatedMiddleware)
def mailing_history_item(request, history_item_id):
    try:
        sender_history = SenderHistory.objects.get(
            id=history_item_id,
            profile=request.user.profile,
        )
    except SenderHistory.DoesNotExist:
        raise Http404

    mongo_client = MongoClient(settings.MONGO_DB_HOST, settings.MONGO_DB_PORT, connect=True)
    mongo_db = mongo_client.mail_sender_2
    mongo_collection = mongo_db.history_items

    history_items = [
        d for d in mongo_collection.find(
            {'sender_history_id': sender_history.id}
        ).sort(
            [('created_at', -1)]
        )
    ]

    mongo_client.close()

    return render(
        request,
        'mailings/history_item.html',
        {
            'breadcumb': generate_breadcumbs([
                {'url': '/', 'title': 'Главная'},
                {'url': '/profile', 'title': 'Профиль'},
                {'url': reverse('mailing_history'), 'title': 'Мои рассылки'},
                {'url': '', 'title': 'Рассылка {}'.format(sender_history.email_account.email)},
            ]),
            'items': history_items,
            'sender_history': sender_history,
        }
    )
