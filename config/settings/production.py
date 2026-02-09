"""
Production settings for Anupam Dutta Portfolio.
"""

from .base import *  # noqa: F401, F403
from decouple import config, Csv

# =============================================================================
# DEBUG
# =============================================================================

DEBUG = False
ALLOWED_HOSTS = config("ALLOWED_HOSTS", cast=Csv())

# =============================================================================
# DATABASE (PostgreSQL for production)
# =============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": config("DB_NAME", default="portfolio_db"),
        "USER": config("DB_USER", default="portfolio_user"),
        "PASSWORD": config("DB_PASSWORD", default=""),
        "HOST": config("DB_HOST", default="localhost"),
        "PORT": config("DB_PORT", default="5432"),
        "CONN_MAX_AGE": 600,
        "OPTIONS": {
            "connect_timeout": 10,
        },
    }
}

# =============================================================================
# SECURITY
# =============================================================================

SECURE_SSL_REDIRECT = config("SECURE_SSL_REDIRECT", default=True, cast=bool)
SECURE_HSTS_SECONDS = config("SECURE_HSTS_SECONDS", default=31536000, cast=int)
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# =============================================================================
# STATIC FILES
# =============================================================================

STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"

# =============================================================================
# EMAIL (SMTP for production)
# =============================================================================

EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"

# =============================================================================
# CORS
# =============================================================================

CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="",
    cast=Csv(),
)

# =============================================================================
# WAGTAIL
# =============================================================================

WAGTAILADMIN_BASE_URL = config("WAGTAILADMIN_BASE_URL")

# =============================================================================
# LOGGING (file-based in production)
# =============================================================================

LOGGING["handlers"]["file"] = {  # noqa: F405
    "class": "logging.handlers.RotatingFileHandler",
    "filename": BASE_DIR / "logs" / "django.log",  # noqa: F405
    "maxBytes": 1024 * 1024 * 5,  # 5MB
    "backupCount": 5,
    "formatter": "verbose",
}
LOGGING["root"]["handlers"] = ["console", "file"]  # noqa: F405
LOGGING["loggers"]["django"]["handlers"] = ["console", "file"]  # noqa: F405
LOGGING["loggers"]["apps"]["handlers"] = ["console", "file"]  # noqa: F405
LOGGING["loggers"]["apps"]["level"] = "WARNING"  # noqa: F405
