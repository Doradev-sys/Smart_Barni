from pathlib import Path
from decouple import config
from datetime import timedelta


BASE_DIR = Path(__file__).resolve().parent.parent.parent


SECRET_KEY = config(
    "SECRET_KEY",
    default="django-secret-key"
)


DEBUG = False


ALLOWED_HOSTS = []


INSTALLED_APPS = [

    # Django apps
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "drf_spectacular",


    # Third party
    "rest_framework",
    "corsheaders",


    # Local apps
    "apps.accounts",
    "apps.menu",
    "apps.inventory",
    "apps.orders",
    "apps.finance",
    "apps.payments",
    "apps.wastage",
    "apps.alerts",
]


AUTH_USER_MODEL = "accounts.User"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": (
        "rest_framework.permissions.IsAuthenticated",
    ),
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
}


SIMPLE_JWT = {

    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=30),

    "REFRESH_TOKEN_LIFETIME": timedelta(days=1),

}


MIDDLEWARE = [

    "django.middleware.security.SecurityMiddleware",

    "django.contrib.sessions.middleware.SessionMiddleware",

    "corsheaders.middleware.CorsMiddleware",

    "django.middleware.common.CommonMiddleware",

    "django.middleware.csrf.CsrfViewMiddleware",

    "django.contrib.auth.middleware.AuthenticationMiddleware",

    "django.contrib.messages.middleware.MessageMiddleware",

    "django.middleware.clickjacking.XFrameOptionsMiddleware",

]


ROOT_URLCONF = "config.urls"


TEMPLATES = [

    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",

        "DIRS": [
            BASE_DIR / "templates"
        ],

        "APP_DIRS": True,

        "OPTIONS": {

            "context_processors": [

                "django.template.context_processors.request",

                "django.contrib.auth.context_processors.auth",

                "django.contrib.messages.context_processors.messages",

            ],

        },

    },

]


WSGI_APPLICATION = "config.wsgi.application"

ASGI_APPLICATION = "config.asgi.application"



DATABASES = {

    "default": {

        "ENGINE": "django.db.backends.postgresql",

        "NAME": config("DB_NAME"),

        "USER": config("DB_USER"),

        "PASSWORD": config("DB_PASSWORD"),

        "HOST": config("DB_HOST"),

        "PORT": config("DB_PORT"),

    }

}



LANGUAGE_CODE = "en-us"


TIME_ZONE = "Africa/Addis_Ababa"


USE_I18N = True


USE_TZ = True



STATIC_URL = "static/"


STATICFILES_DIRS = [

    BASE_DIR / "static"

]



DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
SPECTACULAR_SETTINGS = {
    "TITLE": "Barni Coffee RMS API",
    "DESCRIPTION": "Restaurant Management System API",
    "VERSION": "1.0.0",
}