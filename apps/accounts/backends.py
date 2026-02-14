"""
Custom authentication backend for email-based authentication.
"""

import logging

from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend

logger = logging.getLogger(__name__)

User = get_user_model()


class EmailAuthBackend(ModelBackend):
    """
    Custom authentication backend that uses email instead of username.
    
    Also checks for account lockout status.
    """

    def authenticate(self, request, email=None, password=None, **kwargs):
        """
        Authenticate user by email and password.
        
        Args:
            request: The HTTP request object
            email: User's email address
            password: User's password
            
        Returns:
            User object if authentication successful, None otherwise
        """
        if email is None or password is None:
            return None

        try:
            user = User.objects.get(email=email.lower())
        except User.DoesNotExist:
            # Run the default password hasher to prevent timing attacks
            User().set_password(password)
            return None

        # Check if account is locked
        if user.is_locked:
            logger.warning(f"Login attempt on locked account: {email}")
            return None

        # Check if account is active
        if not user.is_active:
            logger.warning(f"Login attempt on inactive account: {email}")
            return None

        # Verify password
        if user.check_password(password):
            return user

        return None

    def get_user(self, user_id):
        """
        Retrieve user by ID.
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None
