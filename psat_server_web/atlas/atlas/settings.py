"""
Django settings for atlas project.

For more information on this file, see
https://docs.djangoproject.com/en/1.7/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/1.7/ref/settings/
"""

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
import os
from dotenv import load_dotenv

# import forcephot

load_dotenv(override=True)

#from pathlib import Path  # Python 3.6+ only

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
#BASE_DIR = Path(__file__).resolve().parent.parent
#PATHPREFIX = '/sne/atlas'
PATHPREFIX = ''

SITE_ID = 1

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/1.7/howto/deployment/checklist/

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

TEMPLATE_DEBUG = False

ALLOWED_HOSTS = ['*']

ROOT_URLCONF = 'atlas.urls'

WSGI_APPLICATION = 'atlas.wsgi.application'

# 2016-11-07 KWS Fixed the authentication issues by setting cookie names
CSRF_COOKIE_NAME = 'csrf_' + os.environ.get('DJANGO_MYSQL_DBNAME')
SESSION_COOKIE_NAME = 'session_' + os.environ.get('DJANGO_MYSQL_DBNAME')

# 2017-10-03 KWS Had to add this setting because of SSL proxy.
CSRF_TRUSTED_ORIGINS = ['star.pst.qub.ac.uk']

CSRF_FAILURE_VIEW = 'atlas.views.csrf_failure'

LOGIN_REDIRECT_URL = 'home'
LOGIN_URL = 'login'
LOGOUT_URL = 'logout'

# Database
# https://docs.djangoproject.com/en/1.7/ref/settings/#databases

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DJANGO_MYSQL_DBNAME'),
        'USER': os.environ.get('DJANGO_MYSQL_DBUSER'),
        'PASSWORD': os.environ.get('DJANGO_MYSQL_DBPASS'),
        'HOST': os.environ.get('DJANGO_MYSQL_DBHOST'),
        'PORT': int(os.environ.get('DJANGO_MYSQL_DBPORT')),
    }
}


DAEMONS = {
    'tns': {
        'host': os.environ.get('DJANGO_TNS_DAEMON_SERVER'),
        'port': int(os.environ.get('DJANGO_TNS_DAEMON_PORT')),
        'test': True
    },
    'mpc': {
        'host': os.environ.get('DJANGO_MPC_DAEMON_SERVER'),
        'port': int(os.environ.get('DJANGO_MPC_DAEMON_PORT')),
        'test': True
    }
}

# Internationalization
# https://docs.djangoproject.com/en/1.7/topics/i18n/

LANGUAGE_CODE = 'en-us'

TIME_ZONE = 'UTC'

USE_I18N = True

USE_L10N = True

USE_TZ = True



# 2021-05-06 KWS New settings means that if we edit a static file we MUST rerun the collectstatic
#                code to deploy the modified file.

STATIC_URL = PATHPREFIX + '/static/'

# STATICFILES_DIRS tells collectstatic where MY static files are.
STATICFILES_DIRS = (
  os.path.join(BASE_DIR, 'site_media'),
)

STATIC_ROOT = os.path.join(BASE_DIR, 'static')

MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = PATHPREFIX + '/media/'

# All below copied from PS1 web app.

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = (
    'django.template.loaders.filesystem.Loader',
    'django.template.loaders.app_directories.Loader',
)

# 2018-06-06 KWS Added new TEMPLATES settings in place of TEMPLATE_CONTEXT_PROCESSORS
#                and TEMPLATE_DIRS
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            # insert your TEMPLATE_DIRS here
            os.path.join(BASE_DIR, 'templates'),

        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                # Insert your TEMPLATE_CONTEXT_PROCESSORS here or use this
                # list if you haven't customized them:
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
                "django.template.context_processors.debug",
                "django.template.context_processors.i18n",
                "django.template.context_processors.media",
                "django.template.context_processors.request",
                "django.template.context_processors.static",
                "django.template.context_processors.request",
            ],
        },
    },
]

# KWS - Added pagination
MIDDLEWARE = [
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
#    'django.contrib.auth.middleware.SessionAuthenticationMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
#    'pagination.middleware.PaginationMiddleware',
    'django.middleware.security.SecurityMiddleware',
]

ROOT_URLCONF = 'atlas.urls'

# 2015-11-30 KWS Added django-tables2
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.messages',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.sites',
    'django.contrib.staticfiles',
    'atlas',
    # 'pagination',
    'django_tables2',
]