"""
Django settings for dews project.

Generated by "django-admin startproject" using Django 4.2.6.

For more information on this file, see
https://docs.djangoproject.com/en/4.2/topics/settings/

For the full list of settings and their values, see
https://docs.djangoproject.com/en/4.2/ref/settings/
"""

from pathlib import Path
from os import getenv

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

    # custom apps
    "dashboard",
    "sat_data",
]

# Logging
LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "file": {
            "level": "DEBUG",
            "class": "logging.FileHandler",
            "filename": "django.log",
        },
    },
    "loggers": {
        "django": {
            "handlers": ["file"],
            "level": "DEBUG",
            "propagate": True,
        },
    },
}

# Custom Python logger
LOGGER_FILE_LOCATION = BASE_DIR / "backend.log"
LOGGER_FILE_MODE = "w"  # 'w': create new log on every run; 'a': append to existing log
LOGGER_FORMAT = "[%(asctime)s] | %(levelname)s - %(module)s.%(funcName)s[%(lineno)d]: %(message)s"
LOGGER_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOGGER_LEVEL = "DEBUG"

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
                 BASE_DIR / "templates/sat_data"],
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
        "ENGINE": "django.db.backends.postgresql_psycopg2",
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
    BASE_DIR / "static" # dews/static
]

# Media files (Videos, Images, ...)
MEDIA_ROOT = "/dews/media"
MEDIA_URL = "/dews/media/"

# File paths
SAT_DATA_PATH = Path(MEDIA_ROOT) / "sat_data"
EXTRACTED_FILES_PATH = SAT_DATA_PATH / "extracted"
ZIP_FILES_PATH = SAT_DATA_PATH / "zip"
IMAGES_FILES_PATH = SAT_DATA_PATH / "images"

OTHER_FILES_PATH = Path(MEDIA_ROOT) / "other"

FILES_PATH_LIST = [SAT_DATA_PATH, EXTRACTED_FILES_PATH, ZIP_FILES_PATH,
                   IMAGES_FILES_PATH, OTHER_FILES_PATH]

# Default primary key field type
# https://docs.djangoproject.com/en/4.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# Login/Logout
LOGIN_REDIRECT_URL = "/zentrale"
LOGOUT_REDIRECT_URL = "/"