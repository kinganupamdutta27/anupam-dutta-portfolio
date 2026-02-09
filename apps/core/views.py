"""
Core views for error handling and common pages.
"""

import logging

from django.shortcuts import render

logger = logging.getLogger(__name__)


def custom_404(request, exception=None):
    """Custom 404 error page."""
    logger.info(
        f"404 Not Found: {request.path}",
        extra={
            "request_path": request.path,
            "request_method": request.method,
        },
    )
    return render(request, "404.html", status=404)


def custom_500(request):
    """Custom 500 error page."""
    logger.error(
        f"500 Internal Server Error: {request.path}",
        extra={
            "request_path": request.path,
        },
    )
    return render(request, "500.html", status=500)
