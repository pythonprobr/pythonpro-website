"""
Django settings for pythonpro project.

Generated by 'django-admin startproject' using Django 2.0b1.

For more information on this file, see
https://docs.djangoproject.com/en/dev/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import raven
from decouple import config, Csv
from dj_database_url import parse as dburl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/dev/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = config('SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = config('DEBUG', default=False, cast=bool)

ALLOWED_HOSTS = config('ALLOWED_HOSTS', default=[], cast=Csv())

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'pythonpro.core',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'pythonpro.wsgi.application'

# Database
# https://docs.djangoproject.com/en/dev/ref/settings/#databases
default_db_url = 'sqlite:///' + os.path.join(BASE_DIR, 'db.sqlite3')
DATABASES = {
    'default': config('DATABASE_URL', default=default_db_url, cast=dburl),
}

# Password validation
# https://docs.djangoproject.com/en/dev/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/dev/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True

if DEBUG:

    # Static files (CSS, JavaScript, Images)
    # https://docs.djangoproject.com/en/1.11/howto/static-files/

    STATIC_URL = '/static/'
    STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
    MEDIA_URL = '/media/'
    MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
else:

    # STORAGE CONFIGURATION IN S3 AWS
    # ------------------------------------------------------------------------------
    # Uploaded Media Files
    # ------------------------------------------------------------------------------

    INSTALLED_APPS.append('storages', )
    # INSTALLED_APPS.append('s3_folder_storage')

    AWS_ACCESS_KEY_ID = 'Aqui vem a Key Id gerada na AWS'
    AWS_SECRET_ACCESS_KEY = 'Aqui vem o Secret Access Key gerado na AWS '
    AWS_STORAGE_BUCKET_NAME = 'Aqui vem o nome do Buket criado para armazenar os arquivos na AWS'
    AWS_S3_OBJECT_PARAMETERS = {'CacheControl': 'max-age=86400', }
    AWS_PRELOAD_METADATA = True
    AWS_AUTO_CREATE_BUCKET = True
    AWS_QUERYSTRING_AUTH = False

    # AWS cache settings, don't change unless you know what you're doing:
    AWS_EXPIRY = 60 * 60 * 24 * 7

    # Revert the following and use str after the above-mentioned bug is fixed in
    # either django-storage-redux or boto
    control = 'max-age=%d, s-maxage=%d, must-revalidate' % (AWS_EXPIRY, AWS_EXPIRY)

    # Upload Media Folder
    DEFAULT_FILE_STORAGE = 's3_folder_storage.s3.DefaultStorage'
    DEFAULT_S3_PATH = "media"
    MEDIA_ROOT = '/%s/' % DEFAULT_S3_PATH
    MEDIA_URL = '//s3.amazonaws.com/%s/media/' % AWS_STORAGE_BUCKET_NAME

    # Static Assets
    # ------------------------------------------------------------------------------
    STATICFILES_STORAGE = 's3_folder_storage.s3.StaticStorage'
    STATIC_S3_PATH = "static"
    STATIC_ROOT = "/%s/" % STATIC_S3_PATH
    STATIC_URL = '//s3.amazonaws.com/%s/static/' % AWS_STORAGE_BUCKET_NAME
    ADMIN_MEDIA_PREFIX = STATIC_URL + 'admin/'

# Configuring Sentry
SENTRY_DNS = config('SENTRY_DNS', default=None)

if SENTRY_DNS:
    INSTALLED_APPS.append('raven.contrib.django.raven_compat')
    RAVEN_CONFIG = {
        'dsn': SENTRY_DNS,
        # If you are using git, you can also automatically configure the
        # release based on the git info.
        'release': raven.fetch_git_sha(os.path.dirname(os.pardir)),
    }
