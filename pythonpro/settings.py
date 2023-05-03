"""
Django settings for pythonpro project.

Generated by 'django-admin startproject' using Django 2.0b1.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

from functools import partial
from pathlib import Path

import sentry_sdk
from decouple import Csv, config
from dj_database_url import parse as dburl
from sentry_sdk.integrations.celery import CeleryIntegration
from sentry_sdk.integrations.django import DjangoIntegration

# BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE_DIR = Path(__file__).resolve().parent.parent
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

ADMINS = [('Admin', 'admin@dev.pro.br')]

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

# Redirect to HTTPS:
SECURE_SSL_REDIRECT = not DEBUG

SECURE_REFERRER_POLICY = None

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())

PAGARME_CRYPTO_KEY = config('PAGARME_CRYPTO_KEY')
PAGARME_API_KEY = config('PAGARME_API_KEY')

CHAVE_PAGARME_API_PRIVADA = PAGARME_API_KEY
CHAVE_PAGARME_CRIPTOGRAFIA_PUBLICA = PAGARME_CRYPTO_KEY

# Memberkit integration

MEMBERKIT_API_KEY = config('MEMBERKIT_API_KEY')
MEMBERKIT_ON = config('MEMBERKIT_ON', cast=bool, default=False)

# Email Configuration

DEFAULT_FROM_EMAIL = 'suporte@dev.pro.br'

EMAIL_BACKEND = config('EMAIL_BACKEND')
EMAIL_HOST = config('EMAIL_HOST')
EMAIL_PORT = config('EMAIL_PORT', cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD')

# Login Config

LOGIN_REDIRECT_URL = LOGOUT_REDIRECT_URL = '/'
LOGIN_URL = 'two_factor:login'

# 2FA Configs
TWO_FACTOR_PATCH_ADMIN = True

# Recaptch credentials
has_captch_config = config('RECAPTCHA_PUBLIC_KEY')
if has_captch_config:
    RECAPTCHA_PUBLIC_KEY = config('RECAPTCHA_PUBLIC_KEY')
    RECAPTCHA_PRIVATE_KEY = config('RECAPTCHA_PRIVATE_KEY')
    RECAPTCHA_REQUIRED_SCORE = 0.85
else:
    SILENCED_SYSTEM_CHECKS = ['captcha.recaptcha_test_key_error']

# Application definition

INSTALLED_APPS = [
    'pythonpro.core',
    'pythonpro.discourse',
    'pythonpro.discord',
    'pythonpro.modules',
    'pythonpro.cohorts',
    'pythonpro.email_marketing',
    'pythonpro.dashboard',
    'pythonpro.launch',
    'pythonpro.analytics',
    'pythonpro.checkout',
    'pythonpro.redirector',
    'pythonpro.pages',
    'pythonpro.memberkit',
    'captcha',
    'rolepermissions',
    'ordered_model',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'collectfast',
    'django.contrib.staticfiles',
    'django_extensions',
    'bootstrap4',
    'django_pagarme',
    'phonenumber_field',
    'django_otp',
    'django_otp.plugins.otp_static',
    'django_otp.plugins.otp_totp',
    'two_factor',
    'two_factor.plugins.phonenumber',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.gzip.GZipMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

if DEBUG:
    INSTALLED_APPS.append('debug_toolbar')
    MIDDLEWARE.insert(2, 'debug_toolbar.middleware.DebugToolbarMiddleware')
    INTERNAL_IPS = ['127.0.0.1']

ROLEPERMISSIONS_MODULE = 'pythonpro.core.roles'
# Discourse config
DISCOURSE_BASE_URL = config('DISCOURSE_BASE_URL', default='')
DISCOURSE_SSO_SECRET = config('DISCOURSE_SSO_SECRET')
DISCOURSE_API_USER = config('DISCOURSE_API_USER')
DISCOURSE_API_KEY = config('DISCOURSE_API_KEY')

ROOT_URLCONF = 'pythonpro.urls'

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
                'pythonpro.core.context_processors.global_settings',
                'pythonpro.modules.context_processors.global_settings',
            ],
        },
    },
]

WSGI_APPLICATION = 'pythonpro.wsgi.application'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
default_db_url = 'sqlite:///' + str(BASE_DIR / 'db.sqlite3')

if 'localhost' not in ALLOWED_HOSTS:
    dburl = partial(dburl, conn_max_age=600, ssl_require=True)

DEFAULT_AUTO_FIELD = 'django.db.models.AutoField'

DATABASES = {
    'default': config('DATABASE_URL', default=default_db_url, cast=dburl),
}

# Cache configuration
REDIS_URL = config('REDIS_URL')
CACHE_REDIS_URL = f'{REDIS_URL}/1'

CACHE_TTL = 60 * 15

CACHE_TURNED_ON = config('CACHE_TURNED_ON', default=True, cast=bool)

if CACHE_TURNED_ON:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": CACHE_REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient"
            },
            "KEY_PREFIX": "example"
        }
    }
else:
    CACHES = {
        'default': {
            'BACKEND': 'django.core.cache.backends.dummy.DummyCache',
        }
    }

# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME':
            'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME':
            'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

AUTH_USER_MODEL = 'core.User'

# default password for user creation
DEFAULT_USER_CREATION_PASSWORD = config('DEFAULT_USER_CREATION_PASSWORD')

# Internationalization
# https://docs.djangoproject.com/en/dev/topics/i18n/

# for phone validation
PHONENUMBER_DEFAULT_REGION = 'BR'

LANGUAGE_CODE = 'pt-br'

TIME_ZONE = 'America/Sao_Paulo'

USE_I18N = True

USE_L10N = True

USE_TZ = True

# Configuration for dev environment
MEDIA_URL = '/media/'
MEDIA_ROOT = str(BASE_DIR / 'mediafiles')
STATIC_URL = '/static/'
STATIC_ROOT = str(BASE_DIR / 'staticfiles')
COLLECTFAST_ENABLED = False

# STORAGE CONFIGURATION IN S3 AWS
# ------------------------------------------------------------------------------
# Uploaded Media Files
# ------------------------------------------------------------------------------
AWS_ACCESS_KEY_ID = config('DJANGO_AWS_ACCESS_KEY_ID', default=False)
if AWS_ACCESS_KEY_ID:  # pragma: no cover
    COLLECTFAST_ENABLED = True
    STATICFILES_STORAGE = "storages.backends.s3boto3.S3Boto3Storage"
    COLLECTFAST_STRATEGY = "collectfast.strategies.boto3.Boto3Strategy"
    INSTALLED_APPS.append('s3_folder_storage')
    INSTALLED_APPS.append('storages')
    AWS_SECRET_ACCESS_KEY = config('DJANGO_AWS_SECRET_ACCESS_KEY')
    AWS_STORAGE_BUCKET_NAME = config('DJANGO_AWS_STORAGE_BUCKET_NAME')
    AWS_S3_OBJECT_PARAMETERS = {
        'CacheControl': 'max-age=86400',
    }
    AWS_PRELOAD_METADATA = True
    AWS_AUTO_CREATE_BUCKET = False
    AWS_QUERYSTRING_AUTH = True
    AWS_S3_CUSTOM_DOMAIN = None

    AWS_DEFAULT_ACL = 'public-read'

    # AWS cache settings, don't change unless you know what you're doing:
    AWS_EXPIRY = 60 * 60 * 24 * 7

    # Revert the following and use str after the above-mentioned bug is fixed in
    # either django-storage-redux or boto
    control = f'max-age={AWS_EXPIRY:d}, s-maxage={AWS_EXPIRY:d}, must-revalidate'

    # Upload Media Folder
    DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
    DEFAULT_S3_PATH = 'media'
    MEDIA_ROOT = f'/{DEFAULT_S3_PATH}/'
    MEDIA_URL = f'//{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{DEFAULT_S3_PATH}/'

    # Static Assets
    # ------------------------------------------------------------------------------
    STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'
    STATIC_S3_PATH = 'static'
    STATIC_ROOT = f'/{STATIC_S3_PATH}/'
    STATIC_URL = f'//{AWS_STORAGE_BUCKET_NAME}.s3.amazonaws.com/{STATIC_S3_PATH}/'
    ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

# ------------------------------------------------------------------------------

# Configuring Sentry
SENTRY_DSN = config('SENTRY_DSN', default=None)

if SENTRY_DSN:  # pragma: no cover
    sentry_sdk.init(
        dsn=SENTRY_DSN,
        integrations=[DjangoIntegration(), CeleryIntegration()]
    )

# Active Campaign Configuration
ACTIVE_CAMPAIGN_URL = config('ACTIVE_CAMPAIGN_URL')
ACTIVE_CAMPAIGN_KEY = config('ACTIVE_CAMPAIGN_KEY')
ACTIVE_CAMPAIGN_TURNED_ON = config('ACTIVE_CAMPAIGN_TURNED_ON', cast=bool, default=True)

# Google Tag Manager Configuration
GOOGLE_TAG_MANAGER_ID = config('GOOGLE_TAG_MANAGER_ID')

# Discord App Configuration
DISCORD_APP_CLIENT_ID = config('DISCORD_APP_CLIENT_ID')
DISCORD_APP_CLIENT_SECRET = config('DISCORD_APP_CLIENT_SECRET')
DISCORD_APP_BOT_TOKEN = config('DISCORD_APP_BOT_TOKEN')
DISCORD_GUILD_ID = config('DISCORD_GUILD_ID')

# Celery config


CELERY_BROKER_URL = config('CLOUDAMQP_URL')

CELERY_TASK_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE

# Hotzapp configuration
HOTZAPP_API_URL = config('HOTZAPP_API_URL')


# needed to allow iframes in pixeling system
X_FRAME_OPTIONS = 'ALLOWALL'
XS_SHARING_ALLOWED_METHODS = ['GET']

# api key for subscribe users
LOCAL_API_KEY = config('LOCAL_API_KEY', default='')
