import os


PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
PACKAGE_ROOT = os.path.abspath(os.path.dirname(__file__))

DEBUG = True
TEMPLATE_DEBUG = DEBUG

ADMINS = [
    # ("Your Name", "your_email@example.com"),
]

MANAGERS = ADMINS

DATABASES = {
    'default': {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": "dev.db",
    }
}


# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',  
#         'NAME': 'ceni',  
#         'USER': 'root',  
#         'PASSWORD': 'cdn%nf',  
#         'HOST': '192.168.5.120',  
#         'PORT': '3306',  
#     }
# }

# Local time zone for this installation. Choices can be found here:
# http://en.wikipedia.org/wiki/List_of_tz_zones_by_name
# although not all choices may be available on all operating systems.
# On Unix systems, a value of None will cause Django to use the same
# timezone as the operating system.
# If running in a Windows environment this must be set to the same as your
# system time zone.
TIME_ZONE = "UTC"

# Language code for this installation. All choices can be found here:
# http://www.i18nguy.com/unicode/language-identifiers.html
LANGUAGE_CODE = "zh-cn"

SITE_ID = 1

# If you set this to False, Django will make some optimizations so as not
# to load the internationalization machinery.
USE_I18N = True

# If you set this to False, Django will not format dates, numbers and
# calendars according to the current locale.
USE_L10N = True

# If you set this to False, Django will not use timezone-aware datetimes.
USE_TZ = True

# Absolute filesystem path to the directory that will hold user-uploaded files.
# Example: "/home/media/media.lawrence.com/media/"
MEDIA_ROOT = os.path.join(PACKAGE_ROOT, "site_media", "media")

# URL that handles the media served from MEDIA_ROOT. Make sure to use a
# trailing slash.
# Examples: "http://media.lawrence.com/media/", "http://example.com/media/"
MEDIA_URL = "/site_media/media/"

# Absolute path to the directory static files should be collected to.
# Don"t put anything in this directory yourself; store your static files
# in apps" "static/" subdirectories and in STATICFILES_DIRS.
# Example: "/home/media/media.lawrence.com/static/"
STATIC_ROOT = os.path.join(PACKAGE_ROOT, "site_media", "static")

# URL prefix for static files.
# Example: "http://media.lawrence.com/static/"
STATIC_URL = "/site_media/static/"

# Additional locations of static files
STATICFILES_DIRS = [
    os.path.join(PACKAGE_ROOT, "static"),
]

# List of finder classes that know how to find static files in
# various locations.
STATICFILES_FINDERS = [
    "django.contrib.staticfiles.finders.FileSystemFinder",
    "django.contrib.staticfiles.finders.AppDirectoriesFinder",
]

LOCALE_PATHS = [os.path.join(PROJECT_ROOT, 'i18n', app, 'locale') for app in os.listdir(os.path.join(PROJECT_ROOT,'i18n'))]

# Make this unique, and don't share it with anybody.
SECRET_KEY = "2d3di+cxe4f1gh5cewjlpj&amp;qwr^6xi3d91p!blkhz3rl&amp;8hvpx"

# List of callables that know how to import templates from various sources.
TEMPLATE_LOADERS = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]

TEMPLATE_CONTEXT_PROCESSORS = [
    "django.contrib.auth.context_processors.auth",
    "django.core.context_processors.debug",
    "django.core.context_processors.i18n",
    "django.core.context_processors.media",
    "django.core.context_processors.static",
    "django.core.context_processors.tz",
    "django.core.context_processors.request",
    "django.contrib.messages.context_processors.messages",
    "account.context_processors.account",
    "pinax_theme_bootstrap.context_processors.theme",
]


MIDDLEWARE_CLASSES = [
    "django.middleware.common.CommonMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
]

ROOT_URLCONF = "ccf.urls"

# Python dotted path to the WSGI application used by Django's runserver.
WSGI_APPLICATION = "ccf.wsgi.application"

TEMPLATE_DIRS = [
    os.path.join(PACKAGE_ROOT, "templates"),
]

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.sites",
    "django.contrib.messages",
    "django.contrib.staticfiles",

    # theme
    "pinax_theme_bootstrap",
    "django_forms_bootstrap",

    # external
    #'xadmin',
    #'django_extensions',
    'crispy_forms',
    #'reversion',
    "account",
    "metron",
    "eventlog",
    "endless_pagination",

    # project
    "ccf",
    "slice",
    "project",
    "resources",
    "plugins.vt",
    "plugins.ipam",
    "plugins.openflow",
    "plugins.network",
    "invite",
]

CRON_POLLING_FREQUENCY = 5
# A sample logging configuration. The only tangible logging
# performed by this configuration is to send an email to
# the site admins on every HTTP 500 error when DEBUG=False.
# See http://docs.djangoproject.com/en/dev/topics/logging for
# more details on how to customize your logging configuration.
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    'formatters': {
        'standard': {

            'format': '%(asctime)s [%(name)s] [%(pathname)s.%(funcName)s:%(lineno)d] [%(levelname)s]- %(message)s'
        },
    },
    "filters": {
        "require_debug_false": {
            "()": "django.utils.log.RequireDebugFalse"
        }
    },
    "handlers": {
        "mail_admins": {
            "level": "ERROR",
            "filters": ["require_debug_false"],
            "class": "django.utils.log.AdminEmailHandler"
        },
        'ceni_debug': {
            'level':'DEBUG',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': PROJECT_ROOT + '/logs/ceni_debug.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        },
        'ceni_error': {
            'level':'ERROR',
            'class':'logging.handlers.RotatingFileHandler',
            'filename': PROJECT_ROOT + '/logs/ceni_error.log',
            'maxBytes': 1024*1024*5,
            'backupCount': 5,
            'formatter':'standard',
        },
        'console':{
            'level':'DEBUG',
            'class':'logging.StreamHandler',
            'formatter':'standard',
        },
    },
    "loggers": {
        "django.request": {
            "handlers": ["mail_admins"],
            "level": "ERROR",
            "propagate": True,
        },
        "plugins": {
            "handlers": ["console", "ceni_debug"],
            "level": "DEBUG",
            "propagate": True,
        },
    }
}

FIXTURE_DIRS = [
    os.path.join(PROJECT_ROOT, "fixtures"),
]

#EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'

ACCOUNT_OPEN_SIGNUP = True
ACCOUNT_USE_OPENID = False
ACCOUNT_REQUIRED_EMAIL = False
ACCOUNT_EMAIL_VERIFICATION = False
ACCOUNT_EMAIL_AUTHENTICATION = False
ACCOUNT_LOGIN_REDIRECT_URL = "home"
ACCOUNT_LOGOUT_REDIRECT_URL = "home"
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 2

EMAIL_HOST = 'mail.fnic.cn'
EMAIL_PORT = '25'
EMAIL_HOST_USER = 'tengzhifei@fnic.cn'
FROM_EMAIL = 'tengzhifei@fnic.cn'
DEFAULT_FROM_EMAIL = FROM_EMAIL
EMAIL_HOST_PASSWORD = 'fnic123'

AUTHENTICATION_BACKENDS = [
    "account.auth_backends.UsernameAuthenticationBackend",
]

CRISPY_TEMPLATE_PACK = 'bootstrap'

ANONYMOUS_USER_ID = -1

try:
    from ccf.local_settings import *
except ImportError:
    pass
