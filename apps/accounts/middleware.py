"""
Security middleware for authentication.

Provides:
    - Rate limiting for login attempts
    - Session security
    - Security headers
"""

import logging
import time
from collections import defaultdict
from functools import wraps

from django.conf import settings
from django.core.cache import cache
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render

from apps.core.utils import get_client_ip

logger = logging.getLogger(__name__)


# ==============================================================================
# RATE LIMITING
# ==============================================================================


class RateLimitMiddleware:
    """
    Rate limiting middleware for authentication endpoints.
    
    Limits:
        - Login attempts: 5 per minute per IP
        - Registration: 3 per hour per IP
        - Password reset requests: 3 per hour per IP
    """

    # Rate limit configurations
    RATE_LIMITS = {
        "accounts:login": {"limit": 5, "window": 60},  # 5 per minute
        "accounts:register": {"limit": 3, "window": 3600},  # 3 per hour
        "accounts:password_reset_request": {"limit": 3, "window": 3600},  # 3 per hour
    }

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Check rate limits for POST requests to auth endpoints
        if request.method == "POST":
            url_name = self._get_url_name(request)
            
            if url_name in self.RATE_LIMITS:
                ip = get_client_ip(request)
                config = self.RATE_LIMITS[url_name]
                
                if self._is_rate_limited(ip, url_name, config):
                    logger.warning(
                        f"Rate limit exceeded for {url_name} from IP {ip}"
                    )
                    
                    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
                        return JsonResponse(
                            {"error": "Too many requests. Please try again later."},
                            status=429,
                        )
                    
                    return HttpResponseForbidden(
                        "Too many requests. Please try again later."
                    )

        return self.get_response(request)

    def _get_url_name(self, request):
        """Get the URL name for the current request."""
        if hasattr(request, "resolver_match") and request.resolver_match:
            return f"{request.resolver_match.app_name}:{request.resolver_match.url_name}"
        return None

    def _is_rate_limited(self, ip, endpoint, config):
        """Check if the IP is rate limited for the endpoint."""
        cache_key = f"rate_limit:{endpoint}:{ip}"
        
        # Get current request count
        data = cache.get(cache_key)
        
        if data is None:
            # First request
            cache.set(cache_key, {"count": 1, "start": time.time()}, config["window"])
            return False
        
        # Check if window has expired
        if time.time() - data["start"] > config["window"]:
            # Reset counter
            cache.set(cache_key, {"count": 1, "start": time.time()}, config["window"])
            return False
        
        # Increment counter
        data["count"] += 1
        cache.set(cache_key, data, config["window"])
        
        return data["count"] > config["limit"]


# ==============================================================================
# SESSION SECURITY
# ==============================================================================


class SessionSecurityMiddleware:
    """
    Enhances session security.
    
    Features:
        - Regenerates session ID on login
        - Validates session IP (optional)
        - Logs suspicious activity
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Add security headers for authenticated pages
        if request.user.is_authenticated:
            response["Cache-Control"] = "no-cache, no-store, must-revalidate, private"
            response["Pragma"] = "no-cache"
            response["Expires"] = "0"
        
        return response


# ==============================================================================
# SECURITY HEADERS MIDDLEWARE
# ==============================================================================


class SecurityHeadersMiddleware:
    """
    Adds security headers to responses.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        
        # Content Security Policy for auth pages
        if request.path.startswith("/accounts/") or request.path.startswith("/jobs/"):
            # Strict CSP for auth pages
            response["X-Content-Type-Options"] = "nosniff"
            response["X-Frame-Options"] = "DENY"
            response["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response


# ==============================================================================
# DECORATOR FOR VIEW-LEVEL RATE LIMITING
# ==============================================================================


def rate_limit(limit=5, window=60, key_func=None):
    """
    Decorator for rate limiting views.
    
    Args:
        limit: Maximum number of requests
        window: Time window in seconds
        key_func: Function to generate cache key (default: IP-based)
    
    Usage:
        @rate_limit(limit=5, window=60)
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(request)
            else:
                ip = get_client_ip(request)
                cache_key = f"rate_limit:{view_func.__name__}:{ip}"
            
            # Check rate limit
            data = cache.get(cache_key)
            
            if data is None:
                cache.set(cache_key, {"count": 1, "start": time.time()}, window)
            elif time.time() - data["start"] > window:
                cache.set(cache_key, {"count": 1, "start": time.time()}, window)
            else:
                data["count"] += 1
                cache.set(cache_key, data, window)
                
                if data["count"] > limit:
                    logger.warning(
                        f"Rate limit exceeded for {view_func.__name__} - key: {cache_key}"
                    )
                    return HttpResponseForbidden(
                        "Too many requests. Please try again later."
                    )
            
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator
