import bleach
import uuid

from django.conf import settings


allowed_html_tags = [
    'p', 'div', 'span', 'body', 'head', 'html', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'h7', 'b', 'i', 'strong', 'em',
    'img', 'a', 'table', 'thead', 'tbody', 'th', 'td', 'tr', 'br', 'style', 'link', 'doctype', 'meta', 'form', 'input',
    'select', 'textarea', 'button',
]

allowed_html_attributes = ['href', 'src', 'style', 'title', 'class', 'id', ]

ru_months_in = [
    'января', 'февраля', 'марта', 'апреля', 'мая', 'июня',
    'июля', 'августа', 'сентября', 'октября', 'ноября', 'декабря',
]


def get_uuid_string():
    return str(uuid.uuid4()).replace('-', '')


def generate_breadcumbs(breadcumbs_list):
    t = len(breadcumbs_list)
    new_lst = []
    for i in range(0, t-1):
        new_lst.append("<li><a href='{}'>{}</a></li>".format(breadcumbs_list[i]['url'], breadcumbs_list[i]['title']))
    new_lst.append("<li class='active'>{}</a>".format(breadcumbs_list[t-1]['title']))
    return ''.join(new_lst)


def cipher_password(password):
    key = settings.SECRET_KEY
    key_len = len(key)
    ords = [ord(char) for char in password]
    ords_len = len(ords)
    new_password = []
    for i in range(0, ords_len):
        new_password.append(chr(ords[i] + ord(key[i % key_len])))
    return ''.join(new_password)


def decipher_password(password):
    key = settings.SECRET_KEY
    key_len = len(key)
    ords = [ord(char) for char in password]
    ords_len = len(ords)
    new_password = []
    for i in range(0, ords_len):
        new_password.append(chr(ords[i] - ord(key[i % key_len])))
    return ''.join(new_password)


def get_russian_countable_name(count, item_1, item_4, item_5):
    if abs(count) in [11, 12, 13, 14, 15, 16, 17, 18, 19]:
        return item_5
    elif abs(count) % 10 in [0, 5, 6, 7, 8, 9]:
        return item_5
    elif abs(count) % 10 in [2, 3, 4]:
        return item_4
    else:
        return item_1


def printable_russian_date(dt):
    return str(dt.day) + ' ' + ru_months_in[dt.month - 1] + ' ' + str(dt.year) + ' г.'


def printable_russian_datetime(dt):
    return printable_russian_date(dt) + ' {}:{}'.format(('00'+str(dt.hour))[-2:], ('00'+str(dt.minute))[-2:])


def clean_html(html_template):
    '''
    return bleach.clean(
            text=str(html_template),
            tags=allowed_html_tags,
            attributes=allowed_html_attributes,
        )
    '''
    return str(html_template)
