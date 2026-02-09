"""
Custom middleware for the portfolio application.

Provides exception logging, request timing, and security enhancements.
"""

import logging
import time

from django.http import JsonResponse

logger = logging.getLogger(__name__)


class ExceptionLoggingMiddleware:
    """
    Middleware to log unhandled exceptions with request context.

    Catches all unhandled exceptions, logs them with relevant request
    information, and returns appropriate error responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            logger.error(
                f"Unhandled exception: {type(e).__name__}: {e}",
                exc_info=True,
                extra={
                    "request_path": request.path,
                    "request_method": request.method,
                    "user_agent": request.META.get("HTTP_USER_AGENT", ""),
                    "remote_addr": self._get_client_ip(request),
                },
            )
            raise

    def process_exception(self, request, exception):
        """
        Process unhandled exceptions and log them with context.
        """
        logger.error(
            f"Exception on {request.method} {request.path}: "
            f"{type(exception).__name__}: {exception}",
            exc_info=True,
            extra={
                "request_path": request.path,
                "request_method": request.method,
                "remote_addr": self._get_client_ip(request),
            },
        )
        return None  # Let Django handle the response

    @staticmethod
    def _get_client_ip(request):
        """Extract the client IP address from the request."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")


class RequestTimingMiddleware:
    """
    Middleware to measure and log request processing time.

    Adds X-Request-Time header to responses and logs slow requests.
    """

    SLOW_REQUEST_THRESHOLD = 2.0  # seconds

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.monotonic()

        response = self.get_response(request)

        duration = time.monotonic() - start_time
        response["X-Request-Time"] = f"{duration:.4f}s"

        if duration > self.SLOW_REQUEST_THRESHOLD:
            logger.warning(
                f"Slow request: {request.method} {request.path} "
                f"took {duration:.2f}s",
                extra={
                    "request_path": request.path,
                    "request_method": request.method,
                    "duration": duration,
                },
            )

        return response
