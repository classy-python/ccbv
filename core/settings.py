from pathlib import Path

from environs import Env


env = Env()


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = env.str("SECRET_KEY", default="extra-super-secret-development-key")

DEBUG = env.bool("DEBUG", default=False)

ALLOWED_HOSTS = ["*"]


INSTALLED_APPS = [
    # Project
    "cbv",
    # Third Party Apps
    "django_extensions",
    "django_pygmy",
    "sans_db",
    # Django
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.staticfiles",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "core.urls"

TEMPLATES = [
    {
        "BACKEND": "sans_db.template_backends.django_sans_db.DjangoTemplatesSansDB",
        "APP_DIRS": True,
    },
]

WSGI_APPLICATION = "core.wsgi.application"

DATABASES = {"default": env.dj_db_url("DATABASE_URL", default="sqlite:///ccbv.sqlite")}
DEFAULT_AUTO_FIELD = "django.db.models.AutoField"

LANGUAGE_CODE = "en"
TIME_ZONE = "Europe/London"
USE_I18N = False
USE_L10N = False
USE_TZ = False

STATIC_ROOT = BASE_DIR / "staticfiles"
STATIC_URL = "/static/"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

CBV_SOURCES = {
    "django.views.generic": "Generic",
    "django.contrib.formtools.wizard.views": "Wizard",
    "django.contrib.auth.views": "Auth",
    "django.contrib.auth.mixins": "Auth",
}
