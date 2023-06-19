from pathlib import Path

import environ

env = environ.Env()
BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env(
    "SECRET_KEY",
    default="django-insecure-eet3aeru3Ajeim1thieN3ib7caerahnuv0Thuen4le9di4zae2rai1AiW5izuRoh",
)
DEBUG = env("DEBUG", default=False)

ALLOWED_HOSTS = env("ALLOWED_HOSTS", default=[])
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mozilla_django_oidc",
    "school.users",
    "school.pages",
    "school.courses",
    "school.problems",
    "school.trackers",
    "school.imports",
    "django_htmx",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django_htmx.middleware.HtmxMiddleware",
]

ROOT_URLCONF = "school.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
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

WSGI_APPLICATION = "school.wsgi.application"

DATABASES = {
    "default": env.db(),
}

AUTH_USER_MODEL = "users.User"
AUTH_PASSWORD_VALIDATORS = []  # Empty, because we use OIDC
AUTHENTICATION_BACKENDS = [
    "school.users.auth.TrojstenOIDCAB",
    "django.contrib.auth.backends.ModelBackend",
]

OIDC_OP_JWKS_ENDPOINT = env(
    "OIDC_OP_JWKS_ENDPOINT",
    default="https://id.trojsten.sk/oauth/.well-known/jwks.json",
)
OIDC_OP_AUTHORIZATION_ENDPOINT = env(
    "OIDC_OP_AUTHORIZATION_ENDPOINT", default="https://id.trojsten.sk/oauth/authorize/"
)
OIDC_OP_USER_ENDPOINT = env(
    "OIDC_OP_USER_ENDPOINT", default="https://id.trojsten.sk/oauth/userinfo/"
)
OIDC_OP_TOKEN_ENDPOINT = env(
    "OIDC_OP_TOKEN_ENDPOINT", default="https://id.trojsten.sk/oauth/token/"
)
OIDC_RP_SCOPES = "openid email profile"
OIDC_RP_SIGN_ALGO = "RS256"
OIDC_RP_CLIENT_ID = env("OIDC_RP_CLIENT_ID")
OIDC_RP_CLIENT_SECRET = env("OIDC_RP_CLIENT_SECRET")

LOGIN_URL = "oidc_authentication_init"
LOGIN_REDIRECT_URL = "/"
LOGOUT_REDIRECT_URL = "/"

LANGUAGE_CODE = "sk-sk"
TIME_ZONE = "Europe/Bratislava"
USE_I18N = True
USE_TZ = True


# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.0/howto/static-files/

STATIC_URL = "/static/"
STATIC_ROOT = "/app/static/"
STATICFILES_DIRS = [BASE_DIR / "school" / "static"]

DEFAULT_FILE_STORAGE = "school.storages.OverwriteFileSystemStorage"
MEDIA_ROOT = BASE_DIR / "media"
MEDIA_URL = "/media/"

# Default primary key field type
# https://docs.djangoproject.com/en/4.0/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"


SCHOOL_IMPORT_TOKEN = env("SCHOOL_IMPORT_TOKEN")
TESTOVAC_CLIENT = env("TESTOVAC_CLIENT", default="KSP-SCHOOL")
TESTOVAC_HOST = env("TESTOVAC_HOST", default="experiment")
TESTOVAC_PORT = env("TESTOVAC_PORT", default=12347)
TESTOVAC_TOKEN = env("TESTOVAC_TOKEN", default="")


if DEBUG:
    import socket

    INSTALLED_APPS.append("debug_toolbar")
    MIDDLEWARE.insert(0, "debug_toolbar.middleware.DebugToolbarMiddleware")

    # add Docker IPs to INTERNAL_IPS
    hostname, _, ips = socket.gethostbyname_ex(socket.gethostname())
    INTERNAL_IPS = [ip[:-1] + "1" for ip in ips] + ["127.0.0.1"]
