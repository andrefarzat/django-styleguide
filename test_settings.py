# -*- coding: utf-8 -*-
import os

DEBUG = True
SECRET_KEY = 'psst'
SITE_ID = 1

ROOT_URLCONF = 'styleguide.urls'

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
        'USER': '',
        'PASSWORD': '',
        'HOST': '',
        'PORT': '',
    }
}

MIDDLEWARE_CLASSES = (
    'django.middleware.common.CommonMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
)


INSTALLED_APPS = (
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'styleguide',
    'styleguide_mock',
)


TEMPLATE_DIRS = (
    os.path.join(BASE_DIR, 'styleguide_mock', 'other_templates'),
)
