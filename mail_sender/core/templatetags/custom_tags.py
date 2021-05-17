import arrow

from django import template
from django.conf import settings

from core.utils import decipher_password as utils_decipher_password, printable_russian_datetime, printable_russian_date

register = template.Library()


@register.simple_tag
def decipher_password(password):
    return utils_decipher_password(password)


@register.simple_tag
def frontend_datetime(dt):
    return printable_russian_datetime(arrow.get(dt).to(settings.FRONTEND_TIME_ZONE).datetime)


@register.simple_tag
def frontend_date(dt):
    return printable_russian_date(arrow.get(dt).to(settings.FRONTEND_TIME_ZONE).datetime)
