from .base import *  # noqa

ALLOWED_HOSTS = ['autharch.kdl.kcl.ac.uk']

INTERNAL_IPS = INTERNAL_IPS + ['']

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': 'app_autharch_liv',
        'USER': 'app_autharch',
        'PASSWORD': '',
        'HOST': ''
    },
}

SECRET_KEY = ''
