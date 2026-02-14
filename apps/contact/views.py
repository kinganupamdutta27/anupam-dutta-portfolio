"""
Contact form views with AJAX support.

Handles form submission via AJAX POST requests with
CSRF protection, rate limiting, and comprehensive error handling.
"""

import logging

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_POST

from apps.core.utils import get_client_ip

from .forms import ContactForm

logger = logging.getLogger(__name__)


@require_POST
@csrf_protect
def contact_submit(request):
    """
    Handle AJAX contact form submissions.

    Expects:
        - POST request with AJAX header (X-Requested-With: XMLHttpRequest)
        - CSRF token
        - Form fields: name, email, message

    Returns:
        JsonResponse with status, message, and optional errors dict.

    Status codes:
        200: Success
        400: Validation error or bad request
        429: Rate limited
        500: Server error
    """
    try:
        # Verify AJAX request
        is_ajax = (
            request.headers.get("X-Requested-With") == "XMLHttpRequest"
            or request.content_type == "application/x-www-form-urlencoded"
        )
        if not is_ajax:
            logger.warning(
                f"Non-AJAX contact form request from {get_client_ip(request)}"
            )
            return JsonResponse(
                {"status": "error", "message": "Invalid request type."},
                status=400,
            )

        form = ContactForm(request.POST)

        # Check rate limiting before form validation
        client_ip = get_client_ip(request)
        if not form.check_rate_limit(client_ip):
            return JsonResponse(
                {
                    "status": "error",
                    "message": (
                        "Too many submissions. Please wait a while before trying again."
                    ),
                },
                status=429,
            )

        if form.is_valid():
            submission = form.save(commit=False)
            submission.ip_address = client_ip
            submission.user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
            submission.save()

            logger.info(
                f"Contact form submitted: {submission.name} ({submission.email}) "
                f"from IP {client_ip}"
            )

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Thank you! Your message has been sent successfully.",
                }
            )

        # Form validation errors
        errors = {}
        for field, error_list in form.errors.items():
            if field != "__all__":
                errors[field] = error_list[0]

        non_field_errors = form.non_field_errors()
        error_message = (
            non_field_errors[0]
            if non_field_errors
            else "Please correct the errors below."
        )

        return JsonResponse(
            {
                "status": "error",
                "message": error_message,
                "errors": errors,
            },
            status=400,
        )

    except Exception as e:
        logger.error(f"Contact form error: {e}", exc_info=True)
        return JsonResponse(
            {
                "status": "error",
                "message": "An unexpected error occurred. Please try again later.",
            },
            status=500,
        )
