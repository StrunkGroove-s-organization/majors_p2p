from .secrets import NAME_PG, USER_PG, PASSWORD_PG, HOST_PG, PORT_PG
from .secrets import PASSWORD_REDIS, HOST_REDIS, PORT_REDIS, NUMBER_REDIS

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-p0^g3-svhhra(!k))u#=(4g&tvrkrlhow40l-28@j*_f1o583w'

DEBUG = False

ALLOWED_HOSTS = []

INSTALLED_APPS = [
    'base',
    'count_links',

    'mexc',
    'kucoin',
    'okx',
    'huobi',
    'garantex',
    'bitpapa',
    'hodlhodl',
    'beribit',
    'totalcoin',
    'gateio',
    'bybit',
    'bitget',

    # 'django.contrib.admin',
    # 'django.contrib.auth',
    # 'django.contrib.contenttypes',
    # 'django.contrib.sessions',
    # 'django.contrib.messages',
    # 'django.contrib.staticfiles',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'myproject.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'myproject.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': NAME_PG,
        'USER': USER_PG,
        'PASSWORD': PASSWORD_PG,
        'HOST': HOST_PG,
        'PORT': PORT_PG,
    }
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": 
            f'redis://:{PASSWORD_REDIS}@{HOST_REDIS}:'
            f'{PORT_REDIS}/{NUMBER_REDIS}',
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient",
        }
    }
}

# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/

STATIC_URL = 'static/'

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


### REDIS configuration ###

CELERY_BROKER_URL = (
    f'redis://:{PASSWORD_REDIS}@{HOST_REDIS}:{PORT_REDIS}/{NUMBER_REDIS}'
)
CELERY_RESULT_BACKEND = (
    f'redis://:{PASSWORD_REDIS}@{HOST_REDIS}:{PORT_REDIS}/{NUMBER_REDIS}'
)
CELERY_TIMEZONE = 'UTC'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASKSERILIZER =  'json'
