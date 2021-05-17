import json
import os
from kombu import Exchange, Queue
from corsheaders.defaults import default_headers

from django.core.exceptions import ImproperlyConfigured

secrets_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'secrets.json')
with open(secrets_path) as f:
    secrets = json.loads(f.read())


def get_secret(setting, section=None, secrets=secrets):
    try:
        if section:
            return secrets[section][setting]
        return secrets[setting]
    except KeyError:
        key = setting if not section else '%s["%s"]' % (section, setting)
        error_message = 'Ключ {} не найден в конфигурационном файле secrets.json.'.format(key)
        raise ImproperlyConfigured(error_message)


BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SECRET_KEY = get_secret('SECRET_KEY')

DEBUG = False

DOMAIN = get_secret('DOMAIN')
PROTOCOL = get_secret('PROTOCOL')
HTTP_DOMAIN = PROTOCOL + '://' + DOMAIN
ALLOWED_HOSTS = [DOMAIN]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'corsheaders',
    'constance',
    'constance.backends.database',
    'rest_framework',

    'core.apps.CoreConfig',
    'accounts.apps.AccountsConfig',
    'mailings.apps.MailingsConfig',
    'smtp.apps.SmtpConfig',
]

CORS_ORIGIN_ALLOW_ALL = True
CORS_ALLOW_HEADERS = list(default_headers) + ['api-key',]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mail_sender.urls'
APPEND_SLASH = False

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mail_sender.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'HOST': get_secret(section='DATABASE', setting='HOST'),
        'PORT': get_secret(section='DATABASE', setting='PORT'),
        'NAME': get_secret(section='DATABASE', setting='NAME'),
        'USER': get_secret(section='DATABASE', setting='USER'),
        'PASSWORD': get_secret(section='DATABASE', setting='PASSWORD'),
    }
}

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',},
]

LANGUAGE_CODE = 'ru-RU'
TIME_ZONE = 'UTC'
FRONTEND_TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_L10N = True
USE_TZ = True

CONSTANCE_BACKEND = 'constance.backends.database.DatabaseBackend'

CONSTANCE_CONFIG = {
    'ADMIN_EMAILS_LIST': ("", "Список email администраторов, разделённый точкой с запятой (;)", str),
    'ADMIN_EMAILS_FROMNAME': ("mail-sender", "Имя отправителя email от mail-sender", str),
    'FEEDBACK_EMAIL_SUBJECT': ("Обратная связь", "Тема письма для обратной связи", str),
}

STATIC_ROOT = os.path.join(BASE_DIR, 'static/')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media/')

MEDIA_URL = '/media/'
STATIC_URL = '/static/'

os.makedirs(os.path.join(STATIC_ROOT), exist_ok=True)
os.makedirs(os.path.join(MEDIA_ROOT), exist_ok=True)

REDIS_HOST = get_secret(section='REDIS', setting='HOST')
REDIS_PORT = get_secret(section='REDIS', setting='PORT')
REDIS_CACHE_DB = get_secret(section='REDIS', setting='CACHE_DB')

EMAIL_HOST = get_secret(section='EMAIL_SETTINGS', setting='EMAIL_HOST')
EMAIL_PORT = get_secret(section='EMAIL_SETTINGS', setting='EMAIL_PORT')
EMAIL_HOST_USER = get_secret(section='EMAIL_SETTINGS', setting='EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = get_secret(section='EMAIL_SETTINGS', setting='EMAIL_HOST_PASSWORD')
SERVER_EMAIL = get_secret(section='EMAIL_SETTINGS', setting='SERVER_EMAIL')
EMAIL_USE_TLS = True

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://{}:{}/{}".format(
            REDIS_HOST, REDIS_PORT, REDIS_CACHE_DB
        ),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

os.makedirs(os.path.join(BASE_DIR, 'logs'), exist_ok=True)
LOGGING = {
    'version': 1.0,
    'disable_existing_loggers': True,
    'formatters': {
        'simple': {
            'format': '[%(asctime)s: %(levelname)s] %(message)s',
        },
    },
    'handlers': {
        'main_handler': {
            'filename': os.path.join(BASE_DIR, 'logs', 'main.log'),
            'mode': 'a+',
            'class': 'logging.handlers.RotatingFileHandler',
            'formatter': 'simple',
            'maxBytes': 1024 * 1024 * 500,
            'backupCount': 5,
        },
    },
    'loggers': {
        'main': {
            'handlers': ['main_handler'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

MONGO_DB_HOST = get_secret(section='MONGO_DB', setting='HOST')
MONGO_DB_PORT = get_secret(section='MONGO_DB', setting='PORT')

CELERY_BROKER_URL = get_secret(section='CELERY', setting='BROKER_URL')
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'

CELERY_ENABLE_UTC = True
CELERY_TIMEZONE = 'UTC'

CELERY_IGNORE_RESULT = True
CELERY_MAX_TASKS_PER_CHILD = 1
CELERY_WORKER_MAX_TASKS_PER_CHILD = 1
CELERY_MAX_MEMORY_PER_CHILD = 100 * 1024 # 100 MB
CELERY_WORKER_MAX_MEMORY_PER_CHILD = 100 * 1024 # 100 MB

CELERY_TASK_TIME_LIMIT = 120
CELERY_TASK_SOFT_TIME_LIMIT = 60

CELERY_TASK_QUEUES = {
    'high': Queue('high', Exchange('high', type='direct'), routing_key='high'),
    'normal': Queue('normal', Exchange('normal', type='direct'), routing_key='normal'),
    'low': Queue('low', Exchange('low', type='direct'), routing_key='low'),
}
CELERY_TASK_DEFAULT_QUEUE = 'normal'
CELERY_TASK_DEFAULT_EXCHANGE = 'normal'
CELERY_TASK_DEFAULT_ROUTING_KEY = 'normal'
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
