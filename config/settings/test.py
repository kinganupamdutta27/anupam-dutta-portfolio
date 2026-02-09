"""
Test settings for Anupam Dutta Portfolio.

Optimized for fast test execution.
"""

from .base import *  # noqa: F401, F403

# ==============================================================================
# CORE SETTINGS
# ==============================================================================

DEBUG = False
SECRET_KEY = "test-secret-key-not-for-production"
ALLOWED_HOSTS = ["*"]

# ==============================================================================
# DATABASE (SQLite in-memory for fast tests)
# ==============================================================================

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": ":memory:",
    }
}

# ==============================================================================
# PASSWORD HASHERS (Faster hashing for tests)
# ==============================================================================

PASSWORD_HASHERS = [
    "django.contrib.auth.hashers.MD5PasswordHasher",
]

# ==============================================================================
# EMAIL
# ==============================================================================

EMAIL_BACKEND = "django.core.mail.backends.locmem.EmailBackend"

# ==============================================================================
# CACHING (Dummy for tests)
# ==============================================================================

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# ==============================================================================
# STATIC FILES (Simplified for tests)
# ==============================================================================

STATICFILES_STORAGE = "django.contrib.staticfiles.storage.StaticFilesStorage"

# ==============================================================================
# MEDIA (Temp directory for tests)
# ==============================================================================

import tempfile

MEDIA_ROOT = tempfile.mkdtemp()

# ==============================================================================
# LOGGING (Minimal for tests)
# ==============================================================================

LOGGING = {
    "version": 1,
    "disable_existing_loggers": True,
    "handlers": {
        "null": {
            "class": "logging.NullHandler",
        },
    },
    "root": {
        "handlers": ["null"],
        "level": "CRITICAL",
    },
}

# ==============================================================================
# WAGTAIL (Simplified for tests)
# ==============================================================================

WAGTAILADMIN_BASE_URL = "http://localhost:8000"
