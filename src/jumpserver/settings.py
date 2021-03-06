"""
Django settings for jumpserver project.

Generated by 'django-admin startproject' using Django 1.9.6.

For more information on this file, see
https://docs.djangoproject.com/en/1.9/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.9/ref/settings/
"""

import os
import ConfigParser

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

config = ConfigParser.ConfigParser()
config.read(os.path.join(BASE_DIR,'jumserver.conf'))
KEY_DIR = os.path.join(BASE_DIR, 'keys')

# Mail config
MAIL_ENABLE = config.get('mail','mail_enable')
EMAIL_HOST = config.get('mail','email_host')
EMAIL_PORT = config.get('mail','email_port')
EMAIL_HOST_USER = config.get('mail','email_host_user')
EMAIL_HOST_PASSWORD = config.get('mail','email_host_password')
EMAIL_USE_TLS = config.get('mail','email_use_tls')
# EMAIL_USE_SSL = config.get('mail','email_use_ssl')--->Note that EMAIL_USE_TLS/EMAIL_USE_SSL are mutually exclusive, so only set one of those settings to True.
EMAIL_TIMEOUT = 5

# ----------Log----------#
LOG_DIR = os.path.join(BASE_DIR, 'logs')
LOG_LEVEL = config.get('base', 'log')
URL = config.get('base', 'url')

#Connect
try:
    NAV_SORT_BY = config.get('connect','nav_sort_by')
except (ConfigParser.NoSectionError,ConfigParser.NoOptionError):
    NAV_SORT_BY = 'ip'

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.9/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = 'tl9(-e+!bqu0-sy)n^s18z1_#f^v2^nni+b&07&2vb1dot7t27'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = []


AUTH_USER_MODEL = 'juser.User'

# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'juser',
    'jlog',
    'jasset',
    'jumpserver',
    'jperm',
]

MIDDLEWARE_CLASSES = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'jumpserver.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')]
        ,
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

WSGI_APPLICATION = 'jumpserver.wsgi.application'


# Database
# https://docs.djangoproject.com/en/1.9/ref/settings/#databases

DATABASES = {}

if config.get('db','engine') == 'mysql':
    DB_HOST = config.get('db','host')
    DB_PORT = config.get('db','port')
    DB_USER = config.get('db','user')
    DB_PASSWORD = config.get('db','password')
    DB_DATABASE = config.get('db','database')
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': DB_DATABASE,
            'USER':DB_USER,
            'PASSWORD':DB_PASSWORD,
            'HOST':DB_HOST,
            'PORT':DB_PORT,
        }
    }


# Password validation
# https://docs.djangoproject.com/en/1.9/ref/settings/#auth-password-validators

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
# https://docs.djangoproject.com/en/1.9/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'Asia/Shanghai'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/1.9/howto/static-files/

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(os.path.dirname(BASE_DIR),'static_in_env','static_root')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR,'static_in_pro'),
]

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(os.path.dirname(BASE_DIR),'static_in_env','media_root')