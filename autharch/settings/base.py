"""
Django settings for autharch project.

For the full list of settings and their values, see
https://docs.djangoproject.com/en/dev/ref/settings/

For production settings see
https://docs.djangoproject.com/en/dev/howto/deployment/checklist/
"""

import getpass
import logging
import os

from django_auth_ldap.config import LDAPGroupQuery
from kdl_ldap.settings import *  # noqa

# Build paths inside the project like this: os.path.join(BASE_DIR, ...)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

PROJECT_NAME = 'autharch'
PROJECT_TITLE = 'AuthArch'

# -----------------------------------------------------------------------------
# Core Settings
# https://docs.djangoproject.com/en/dev/ref/settings/#id6
# -----------------------------------------------------------------------------

ADMINS = ()
MANAGERS = ADMINS

ALLOWED_HOSTS = []

# https://docs.djangoproject.com/en/dev/ref/settings/#caches
# https://docs.djangoproject.com/en/dev/topics/cache/
# http://redis.io/topics/lru-cache
# http://niwibe.github.io/django-redis/
CACHE_REDIS_DATABASE = '0'

CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/' + CACHE_REDIS_DATABASE,
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'IGNORE_EXCEPTIONS': True
        }
    }
}


CSRF_COOKIE_SECURE = True

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# -----------------------------------------------------------------------------
# EMAIL SETTINGS
# -----------------------------------------------------------------------------

DEFAULT_FROM_EMAIL = 'noreply@kcl.ac.uk'
EMAIL_HOST = 'smtp.cch.kcl.ac.uk'
EMAIL_PORT = 25
EMAIL_HOST_USER = ''
EMAIL_HOST_PASSWORD = ''
EMAIL_SUBJECT_PREFIX = '[Django {}] '.format(PROJECT_NAME)
EMAIL_USE_TLS = False

# Sender of error messages to ADMINS and MANAGERS
SERVER_EMAIL = DEFAULT_FROM_EMAIL

INSTALLED_APPS = [
    'adminactions',
    'polymorphic',

    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.gis',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'compressor',
    'corsheaders',
    'django_extensions',
    'django_filters',
    'kdl_ldap',
    'modelcluster',
    'rest_framework',
    'rest_framework.authtoken',
    'taggit',

    'wagtail.core',
    'wagtail.admin',
    'wagtail.documents',
    'wagtail.snippets',
    'wagtail.users',
    'wagtail.images',
    'wagtail.embeds',
    'wagtail.contrib.redirects',
    'wagtail.contrib.settings',
    'wagtail.contrib.forms',
    'wagtail.sites',
    'wagtail.contrib.routable_page',
    'wagtail.contrib.table_block'
]

INSTALLED_APPS += [
    'archival.apps.ArchivalConfig',
    'authority.apps.AuthorityConfig',
    'ckeditor',
    'countries_plus',
    'geonames_place.apps.GeonamesPlaceConfig',
    'autharch.apps.AuthArchAdminConfig',
    'jargon.apps.JargonConfig',
    'kdl_wagtail.core',
    'languages_plus',
    'media.apps.MediaConfig',
    'nested_admin',
    'reversion',
    'script_codes.apps.ScriptCodesConfig',
    'scm.apps.ScmConfig',
    'editor.apps.EditorConfig',
    'haystack',

    # keep this as the last app
    'hal.apps.HalConfig'
]

INTERNAL_IPS = ['127.0.0.1']

# https://docs.djangoproject.com/en/dev/topics/i18n/
LANGUAGE_CODE = 'en-gb'
TIME_ZONE = 'Europe/London'
USE_I18N = True
USE_L10N = False
USE_TZ = True

LOGGING_ROOT = os.path.join(BASE_DIR, 'logs')
LOGGING_LEVEL = logging.WARNING

if not os.path.exists(LOGGING_ROOT):
    os.makedirs(LOGGING_ROOT)

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': ('%(levelname)s %(asctime)s %(module)s '
                       '%(process)d %(thread)d %(message)s')
        },
        'simple': {
            'format': '%(levelname)s %(message)s'
        }
    },
    'handlers': {
        'file': {
            'level': 'DEBUG',
            'class': 'logging.handlers.TimedRotatingFileHandler',
            'filename': os.path.join(LOGGING_ROOT, 'django.log'),
            'formatter': 'verbose'
        },
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'simple'
        },
        'mail_admins': {
            'level': 'ERROR',
            'class': 'django.utils.log.AdminEmailHandler'
        }
    },
    'loggers': {
        'django': {
            'handlers': ['file', 'mail_admins'],
            'level': LOGGING_LEVEL,
            'propagate': True
        },
        'autharch': {
            'handlers': ['file'],
            'level': LOGGING_LEVEL,
            'propagate': True
        },
        'elasticsearch': {
            'handlers': ['file'],
            'level': LOGGING_LEVEL,
            'propagate': True
        },
        'archival': {
            'handlers': ['console'],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
        'authority': {
            'handlers': ['console'],
            'level': LOGGING_LEVEL,
            'propagate': True,
        },
    }
}

MIDDLEWARE = [
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',

    'wagtail.core.middleware.SiteMiddleware',
    'wagtail.contrib.redirects.middleware.RedirectMiddleware',
]

ROOT_URLCONF = PROJECT_NAME + '.urls'

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = ''

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.contrib.auth.context_processors.auth',
                'django.template.context_processors.debug',
                'django.template.context_processors.media',
                'django.template.context_processors.request',
                'django.template.context_processors.static',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = PROJECT_NAME + '.wsgi.application'

# -----------------------------------------------------------------------------
# Authentication
# https://docs.djangoproject.com/en/dev/ref/settings/#auth
# -----------------------------------------------------------------------------

LOGIN_REDIRECT_URL = 'editor:home'
LOGIN_URL = 'editor:login'
LOGOUT_REDIRECT_URL = 'editor:login'

# -----------------------------------------------------------------------------
# Sessions
# https://docs.djangoproject.com/en/dev/ref/settings/#sessions
# -----------------------------------------------------------------------------

SESSION_COOKIE_SECURE = True

# -----------------------------------------------------------------------------
# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/dev/howto/static-files/
# https://docs.djangoproject.com/en/dev/ref/settings/#static-files
# -----------------------------------------------------------------------------

STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, STATIC_URL.strip('/'))

if not os.path.exists(STATIC_ROOT):
    os.makedirs(STATIC_ROOT)

STATICFILES_DIRS = (os.path.join(BASE_DIR, 'assets'),)

STATICFILES_FINDERS = (
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
)

MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, MEDIA_URL.strip('/'))

if not os.path.exists(MEDIA_ROOT):
    os.makedirs(MEDIA_ROOT)

# -----------------------------------------------------------------------------
# Installed Applications Settings
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Django Compressor
# http://django-compressor.readthedocs.org/en/latest/
# -----------------------------------------------------------------------------

COMPRESS_ENABLED = True

COMPRESS_CSS_FILTERS = [
    # CSS minimizer
    'compressor.filters.cssmin.CSSMinFilter'
]

COMPRESS_PRECOMPILERS = (
    ('text/x-scss', 'django_libsass.SassCompiler'),
)

# -----------------------------------------------------------------------------
# FABRIC
# -----------------------------------------------------------------------------

FABRIC_USER = getpass.getuser()

# -----------------------------------------------------------------------------
# GLOBALS FOR JS
# -----------------------------------------------------------------------------

# Google Analytics ID
GA_ID = ''

CKEDITOR_BASEPATH = STATIC_URL + 'ckeditor/ckeditor/'
CKEDITOR_UPLOAD_PATH = 'uploads/'

# -----------------------------------------------------------------------------
# Automatically generated settings
# -----------------------------------------------------------------------------

# Check which db engine to use:
db_engine = 'django.db.backends.postgresql_psycopg2'
if 'django.contrib.gis' in INSTALLED_APPS:
    db_engine = 'django.contrib.gis.db.backends.postgis'


AUTH_LDAP_REQUIRE_GROUP = (
    (
        LDAPGroupQuery('cn=kdl-staff,' + LDAP_BASE_OU) |
        LDAPGroupQuery('cn=georgian,' + LDAP_BASE_OU)
    )
)

WAGTAIL_SITE_NAME = PROJECT_TITLE
ITEMS_PER_PAGE = 10

REST_FRAMEWORK = {
    'DEFAULT_PAGINATION_CLASS':
        'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework.authentication.TokenAuthentication',
        'rest_framework.authentication.SessionAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
}

# Geonames.
GEONAMES_MAX_RESULTS = 20


# Haystack.
HAYSTACK_CONNECTIONS = {
    'default': {
        'ENGINE': 'haystack.backends.elasticsearch2_backend.Elasticsearch2SearchEngine',  # noqa
        'URL': 'http://127.0.0.1:9200/',
        'INDEX_NAME': 'haystack',
    },
}
HAYSTACK_SEARCH_RESULTS_PER_PAGE = None
HAYSTACK_SIGNAL_PROCESSOR = 'editor.signals.HaystackRealtimeSignalProcessor'


ARCHIVAL_RIGHTS_DECLARATION = """
<p>
Images: © HM Queen Elizabeth II - <a
href="https://creativecommons.org/licenses/by-nc-sa/4.0/">CC BY-NC-SA 4.0</a>
</p>
<p>
Metadata: <a
href="https://creativecommons.org/share-your-work/public-domain/cc0/">CC0</a>
</p>
<p xmlns:dct="http://purl.org/dc/terms/"
xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
<a rel="license"
href="http://creativecommons.org/publicdomain/zero/1.0/">
<img src="http://i.creativecommons.org/p/zero/1.0/88x31.png"
style="border-style: none;" alt="CC0" />
</a>
<br />
To the extent possible under law,
<a rel="dct:publisher"
href="https://georgianpapers.com/">
<span property="dct:title">the Georgian Papers Programme</span></a>
has waived all copyright and related or neighboring rights to
this work.
This work is published from:
<span property="vcard:Country" datatype="dct:ISO3166"
content="GB" about="https://georgianpapers.com/">
United Kingdom</span>.
</p>

Other copyright considerations: Check Credit field for copyright
statements for those items that are not under Crown copyright, for example
unpublished manuscripts by non-royals.
"""

AUTHORITY_RIGHTS_DECLARATION = """
<p>
<a
href="https://creativecommons.org/share-your-work/public-domain/cc0/">CC0</a>
unless specified (in the case of biographical or administrative data drawn
from non-GPP sources).
</p>
<p xmlns:dct="http://purl.org/dc/terms/"
xmlns:vcard="http://www.w3.org/2001/vcard-rdf/3.0#">
<a rel="license"
href="http://creativecommons.org/publicdomain/zero/1.0/">
<img src="http://i.creativecommons.org/p/zero/1.0/88x31.png"
style="border-style: none;" alt="CC0" />
</a>
<br />
To the extent possible under law,
<a rel="dct:publisher"
href="https://georgianpapers.com/">
<span property="dct:title">the Georgian Papers Programme</span></a>
has waived all copyright and related or neighboring rights to
this work.
This work is published from:
<span property="vcard:Country" datatype="dct:ISO3166"
content="GB" about="https://georgianpapers.com/">
United Kingdom</span>.
</p>
"""

AUTHORITY_RIGHTS_DECLARATION_CITATION = 'https://creativecommons.org/publicdomain/zero/1.0/'  # noqa
