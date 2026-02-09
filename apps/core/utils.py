"""
Utility functions for the portfolio application.

Provides common helper functions used across multiple apps.
"""

import logging
import re
from typing import Optional

from django.utils.text import slugify as django_slugify

logger = logging.getLogger(__name__)


def get_client_ip(request) -> str:
    """
    Extract client IP address from the request object.

    Handles X-Forwarded-For headers for reverse proxy setups.

    Args:
        request: Django HTTP request object.

    Returns:
        str: Client IP address or 'unknown' if not determinable.
    """
    try:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")
    except (AttributeError, IndexError):
        return "unknown"


def truncate_text(text: str, max_length: int = 100, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length, appending a suffix.

    Args:
        text: The text to truncate.
        max_length: Maximum length before truncation.
        suffix: String to append to truncated text.

    Returns:
        str: Truncated text with suffix, or original text if shorter.
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)].rsplit(" ", 1)[0] + suffix


def sanitize_string(value: str) -> str:
    """
    Sanitize a string by removing potentially dangerous characters.

    Args:
        value: The string to sanitize.

    Returns:
        str: Sanitized string.
    """
    if not value:
        return ""
    # Remove HTML tags
    clean = re.sub(r"<[^>]+>", "", value)
    # Remove excessive whitespace
    clean = re.sub(r"\s+", " ", clean).strip()
    return clean


def generate_unique_slug(model_class, value: str, slug_field: str = "slug") -> str:
    """
    Generate a unique slug for a model instance.

    Args:
        model_class: The Django model class.
        value: The value to slugify.
        slug_field: The name of the slug field.

    Returns:
        str: A unique slug string.
    """
    slug = django_slugify(value)
    unique_slug = slug
    counter = 1

    while model_class.objects.filter(**{slug_field: unique_slug}).exists():
        unique_slug = f"{slug}-{counter}"
        counter += 1

    return unique_slug


def format_file_size(size_bytes: int) -> str:
    """
    Format file size in bytes to a human-readable string.

    Args:
        size_bytes: File size in bytes.

    Returns:
        str: Human-readable file size string.
    """
    if size_bytes < 0:
        return "0 B"

    units = ["B", "KB", "MB", "GB", "TB"]
    unit_index = 0
    size = float(size_bytes)

    while size >= 1024 and unit_index < len(units) - 1:
        size /= 1024
        unit_index += 1

    return f"{size:.1f} {units[unit_index]}"
