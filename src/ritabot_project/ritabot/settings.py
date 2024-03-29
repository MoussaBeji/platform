"""
Django settings for ritabot project.

Generated by 'django-admin startproject' using Django 2.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/2.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/2.2/ref/settings/
"""

import os

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/2.2/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7mln%8@mw0$^+e@fzjqd_j$(5cu&ettuu-4cglo18m9puzybix'

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

#ALLOWED_HOSTS = ['dev.ritabot.io']
ALLOWED_HOSTS = ['*']


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework', #add the rest framework to the installed apps
    'rest_framework.authtoken', # add the auth token from the rest framework
    'corsheaders',
    'ProfileManager',
    'AgentManager',
    'analytics',
    'commentary',
    'external_api',
    'django_extensions',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.BrokenLinkEmailsMiddleware',
    'django.middleware.common.CommonMiddleware',
]

ROOT_URLCONF = 'ritabot.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ['templates'],
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

WSGI_APPLICATION = 'ritabot.wsgi.application'

if DEBUG:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': 'rita_db',
            'USER': 'django',
            'PASSWORD': 'ritabot2020',
            'HOST': 'localhost'
        }
    }


# Password validation

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
# https://docs.djangoproject.com/en/2.2/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/2.2/howto/static-files/

STATIC_URL = '/static/'
"""For images and files"""
MEDIA_URL =  '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, "media")
#MEDIA_ROOT="/media/"

"""Add the default user_model"""
AUTH_USER_MODEL = 'ProfileManager.UserProfile'

"""     Add the email configuration     """

EMAIL_HOST = 'smtp.solixy.com'
EMAIL_PORT = 587
EMAIL_HOST_USER = 'noreply@solixy.com'
EMAIL_HOST_PASSWORD = 'mGht8KB3J8CDbKRW'
EMAIL_USE_TLS = True
if DEBUG:
    urlServer="http://127.0.0.1/"
else:
    urlServer="https://dev.ritabot.io/"
    urlServer2="https://dev.ritabot.io"

CORS_ORIGIN_ALLOW_ALL = True
# CORS_ORIGIN_ALLOW_ALL = False
#
# CORS_ORIGIN_WHITELIST = (
#        'http://dev.ritabot.io:9001',
#     'https://dev.ritabot.io'
# )
CORS_ALLOW_METHODS = [
   'DELETE',
   'GET',
   'OPTIONS',
   'PATCH',
   'POST',
   'PUT',
]

# SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
# SECURE_SSL_REDIRECT = True
# SESSION_COOKIE_SECURE = True
# CSRF_COOKIE_SECURE = True


"""Const initialisation"""
if DEBUG:
    AGENT_IMAGES_URL = '127.0.0.1:8000'
else:
    AGENT_IMAGES_URL = urlServer2 +':8000'
DEBUG=True



create_service_url = "http://3.133.96.47:8000/api/instance/{}/services/"
update_service_url = "http://3.133.96.47:8000/api/instance/{}/services/{}/"
token_admin_url_dashboard = "c57d8eb5f4d2a7ea19aad60a1aaf300271026a27"


