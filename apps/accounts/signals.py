"""
Signals for the accounts app.
"""

import logging

from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.dispatch import receiver

logger = logging.getLogger(__name__)


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login."""
    ip = request.META.get("REMOTE_ADDR", "unknown")
    logger.info(f"User logged in: {user.email} from IP {ip}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout."""
    if user:
        logger.info(f"User logged out: {user.email}")


@receiver(user_login_failed)
def log_user_login_failed(sender, credentials, request, **kwargs):
    """Log failed login attempt."""
    ip = request.META.get("REMOTE_ADDR", "unknown") if request else "unknown"
    email = credentials.get("email", "unknown")
    logger.warning(f"Failed login attempt for {email} from IP {ip}")
