"""
Development settings for Anupam Dutta Portfolio.
"""

from .base import *  # noqa: F401, F403

# =============================================================================
# DEBUG
# =============================================================================

DEBUG = True
ALLOWED_HOSTS = ["*"]

# =============================================================================
# DATABASE (SQLite for development)
# =============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",  # noqa: F405
    }
}

# =============================================================================
# STATIC FILES (no compression in development)
# =============================================================================

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# =============================================================================
# EMAIL (console backend for development)
# =============================================================================

EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# =============================================================================
# CSRF
# =============================================================================

CSRF_TRUSTED_ORIGINS = ["http://localhost:8000", "http://127.0.0.1:8000"]

# =============================================================================
# WAGTAIL
# =============================================================================

WAGTAILADMIN_BASE_URL = "http://localhost:8000"

# =============================================================================
# LOGGING (more verbose in development)
# =============================================================================

LOGGING["loggers"]["apps"]["level"] = "DEBUG"  # noqa: F405
LOGGING["loggers"]["django"]["level"] = "DEBUG"  # noqa: F405
