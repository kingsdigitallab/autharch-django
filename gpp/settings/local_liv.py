from .base import *  # noqa

ALLOWED_HOSTS = ['gpp.kdl.kcl.ac.uk']

INTERNAL_IPS = INTERNAL_IPS + ['']

DATABASES = {
    'default': {
        'ENGINE': db_engine,
        'NAME': 'app_gpp_liv',
        'USER': 'app_gpp',
        'PASSWORD': '',
        'HOST': ''
    },
}

SECRET_KEY = ''
