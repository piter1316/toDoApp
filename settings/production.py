from .common import *

DEBUG = False

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': 'mQEFKcmB7i',
        'USER': 'mQEFKcmB7i',
        'PASSWORD': 'bP5U2mqHqM',
        'HOST': 'remotemysql.com',  # Or an IP Address that your DB is hosted on
        'PORT': '3306',
    }
}

ALLOWED_HOSTS = ['piter1316.pythonanywhere.com',
                 'remotemysql.com']
