"""
Django settings for dews project.

Generated by "django-admin startproject" using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from os import getenv

# DEWS application"s version
VERSION = "0.0.1"

# Build paths inside the project like this: BASE_DIR / "subdir".
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# See https://docs.djangoproject.com/en/4.2/howto/deployment/checklist/

# SECURITY WARNING: don"t run with debug turned on in production!
DEBUG = getenv("DEBUG")

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = getenv("SECRET_KEY")

# Allowed hosts
ALLOWED_HOSTS = ["*"]

# Trusted origins
CSRF_TRUSTED_ORIGINS = ["http://localhost",
                        "https://localhost"
                        "http://127.0.0.1",
                        "https://127.0.0.1",
                        "http://0.0.0.0",
                        "https://0.0.0.0",
                        ]


# Application definition
INSTALLED_APPS = [
    # Django
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",

    # custom apps
    "dashboard",
    "sat_data",
    "utils",
]

# Logging
if DEBUG:
    LOGGER_LEVEL_CONSOLE = "DEBUG"
else:
    LOGGER_LEVEL_CONSOLE = "INFO"
LOGGER_LEVEL_FILE = "INFO"
LOGGER_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_FILE_PATH = BASE_DIR / "django.log"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "verbose": {
            "format": "[{asctime}] | {levelname} - {module}.{funcName}[{lineno:d}]: {message}",
            "style": "{",
        },
        "simple": {
            "format": "{levelname}|{module}.{funcName}[{lineno:d}]: {message}",
            "style": "{",
        },
    },
    "handlers": {
        "file": {
            "class": "logging.FileHandler",
            "filename": LOG_FILE_PATH,
            "formatter": "verbose",
        },
        "console": {
            "class": "logging.StreamHandler",
            "formatter": "simple",
        },
        "null": {
            "class": "logging.NullHandler",
            "formatter": "simple",
        }
    },
    "loggers": {
        "django": {
            "handlers": ["console", "file"],
            "level": "DEBUG",
            "propagate": True,
        },
        "django.db.backends": {
            # "handlers": ["null"], # deactivates SQL query logs
            "handlers": ["console"], # deactivates SQL query logs
            "level": "DEBUG",
            "propagate": False,
        }
    },
}

# Middleware
MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

# Url conf
ROOT_URLCONF = "dews.urls"

# Templates
TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates",
                 BASE_DIR / "templates/base",
                 BASE_DIR / "templates/sat_data",
                 BASE_DIR / "templates/accounts",],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

# Wsgi
WSGI_APPLICATION = "dews.wsgi.application"


# Database
# https://docs.djangoproject.com/en/4.2/ref/settings/#databases
DB_HOST = "dews-db"
DB_PORT = 5432
DB_NAME = "dews"
DB_USER = "dews"
DB_PASSWORD = "dews"
DB_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

DATABASES = {
    "default": {
        "ENGINE": "django.contrib.gis.db.backends.postgis",
        "NAME": DB_NAME,
        "USER": DB_USER,
        "PASSWORD": DB_PASSWORD,
        "HOST": "dews-db",
        "PORT": DB_PORT
    }
}


# Password validation
# https://docs.djangoproject.com/en/4.2/ref/settings/#auth-password-validators

AUTH_PASSWORD_VALIDATORS = [
    {
        "NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.MinimumLengthValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.CommonPasswordValidator",
    },
    {
        "NAME": "django.contrib.auth.password_validation.NumericPasswordValidator",
    },
]


# Internationalization
# https://docs.djangoproject.com/en/4.2/topics/i18n/

LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.2/howto/static-files/
# Static files will be exported from directories from STATICFILES_DIR to the STATIC_ROOT
STATIC_ROOT = "/dews/static/"
STATIC_URL = "/dews/static/"
STATICFILES_DIRS = [
    BASE_DIR / "static"  # dews/static
]

# Media files (Videos, Images, ...)
DATA_UPLOAD_MAX_MEMORY_SIZE = 10485760000  # 10 GB
FILE_UPLOAD_MAX_MEMORY_SIZE = 10485760000  # 10 GB
MEDIA_ROOT = "/dews/media"
MEDIA_URL = "/dews/media/"

# File paths
SAT_DATA_PATH = Path(MEDIA_ROOT) / "sat_data"
EXTRACTED_FILES_PATH = SAT_DATA_PATH / "extracted"
ARCHIVE_FILES_PATH = SAT_DATA_PATH / "archive"
IMAGES_FILES_PATH = SAT_DATA_PATH / "images"

OTHER_FILES_PATH = Path(MEDIA_ROOT) / "other"

FILES_PATH_LIST = [SAT_DATA_PATH, EXTRACTED_FILES_PATH, ARCHIVE_FILES_PATH,
                   IMAGES_FILES_PATH, OTHER_FILES_PATH]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login/Logout
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/accounts/login/"
