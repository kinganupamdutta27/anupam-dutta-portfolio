"""
Custom template tags and filters for the portfolio application.

Provides reusable template utilities for rendering dynamic content.
"""

import json
import logging

from django import template
from django.utils.safestring import mark_safe

logger = logging.getLogger(__name__)

register = template.Library()


@register.simple_tag(takes_context=True)
def get_site_config(context):
    """
    Retrieve site configuration from Wagtail settings.

    Usage: {% get_site_config as site_config %}
    """
    try:
        from apps.home.models import SiteConfiguration

        request = context.get("request")
        if request:
            return SiteConfiguration.for_request(request)
    except Exception as e:
        logger.error(f"Error retrieving site configuration: {e}")
    return None


@register.filter
def to_json(value):
    """
    Convert a Python list/dict to JSON string for use in JavaScript.

    Usage: {{ typing_texts|to_json }}
    """
    try:
        return mark_safe(json.dumps(value))
    except (TypeError, ValueError) as e:
        logger.error(f"Error converting value to JSON: {e}")
        return "[]"


@register.filter
def icon_for_platform(platform):
    """
    Return the Font Awesome icon class for a given social platform.

    Usage: {{ social_link.platform|icon_for_platform }}
    """
    platform_icons = {
        "linkedin": "fab fa-linkedin-in",
        "github": "fab fa-github",
        "twitter": "fab fa-x-twitter",
        "email": "fas fa-envelope",
        "website": "fas fa-globe",
        "youtube": "fab fa-youtube",
        "instagram": "fab fa-instagram",
        "phone": "fas fa-phone",
    }
    return platform_icons.get(platform, "fas fa-link")


@register.filter
def split_text(value, delimiter=","):
    """
    Split a string by delimiter and return a list.

    Usage: {{ "Python,Django,FastAPI"|split_text }}
    """
    if not value:
        return []
    return [item.strip() for item in value.split(delimiter) if item.strip()]


@register.inclusion_tag("includes/section_header.html")
def section_header(label, title, title_highlight):
    """
    Render a section header with label, title, and highlighted text.

    Usage: {% section_header "About Me" "Passionate about" "Innovative Solutions" %}
    """
    return {
        "label": label,
        "title": title,
        "title_highlight": title_highlight,
    }


@register.simple_tag
def typing_texts_json(page):
    """
    Return typing texts as a JSON array for JavaScript consumption.

    Usage: {% typing_texts_json page as texts_json %}
    """
    try:
        texts = list(page.hero_typing_texts.values_list("text", flat=True))
        return mark_safe(json.dumps(texts))
    except Exception as e:
        logger.error(f"Error generating typing texts JSON: {e}")
        return mark_safe("[]")
