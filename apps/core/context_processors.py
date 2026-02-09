"""
Global context processors for the portfolio application.

These provide data available in all templates.
"""

import logging
from datetime import datetime

from django.conf import settings

logger = logging.getLogger(__name__)


def global_context(request):
    """
    Provide global context variables to all templates.

    Returns:
        dict: Context variables including site configuration and metadata.
    """
    try:
        context = {
            "SITE_NAME": getattr(settings, "WAGTAIL_SITE_NAME", "Portfolio"),
            "CURRENT_YEAR": datetime.now().year,
            "DEBUG": settings.DEBUG,
            "IS_PRODUCTION": not settings.DEBUG,
        }
        return context
    except Exception as e:
        logger.error(f"Error in global_context processor: {e}", exc_info=True)
        return {
            "SITE_NAME": "Portfolio",
            "CURRENT_YEAR": datetime.now().year,
        }
