"""
Custom User model and authentication-related models.

Security Features:
    - Custom User model with email as primary identifier
    - Account lockout after failed login attempts
    - Login history tracking
    - Password reset request system (admin-controlled)
    - Email verification support
"""

import secrets
import logging
from datetime import timedelta

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import MinLengthValidator
from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


# ==============================================================================
# CUSTOM USER MANAGER
# ==============================================================================


class CustomUserManager(BaseUserManager):
    """
    Custom user manager where email is the unique identifier.
    """

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a regular user with the given email and password."""
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        """Create and save a superuser with the given email and password."""
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("is_active", True)
        extra_fields.setdefault("is_verified", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self.create_user(email, password, **extra_fields)


# ==============================================================================
# CUSTOM USER MODEL
# ==============================================================================


class User(AbstractUser):
    """
    Custom User model with email as the primary identifier.
    
    Security features:
        - Account lockout after failed attempts
        - Email verification
        - Login tracking
    """

    # Remove username field, use email instead
    username = None
    email = models.EmailField(
        "email address",
        unique=True,
        error_messages={
            "unique": "A user with that email already exists.",
        },
    )

    # Profile fields
    full_name = models.CharField(
        max_length=255,
        validators=[MinLengthValidator(2)],
        help_text="Your full name.",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Phone number (optional).",
    )
    company = models.CharField(
        max_length=255,
        blank=True,
        help_text="Company or organization name.",
    )
    bio = models.TextField(
        blank=True,
        max_length=500,
        help_text="Brief bio or description.",
    )
    profile_image = models.ImageField(
        upload_to="profiles/",
        blank=True,
        null=True,
    )

    # Security fields
    is_verified = models.BooleanField(
        default=False,
        help_text="Designates whether the user has verified their email.",
    )
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts.",
    )
    lockout_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Account locked until this time.",
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
    )
    last_password_change = models.DateTimeField(
        null=True,
        blank=True,
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["full_name"]

    objects = CustomUserManager()

    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        ordering = ["-created_at"]

    def __str__(self):
        return self.email

    def get_full_name(self):
        return self.full_name or self.email

    def get_short_name(self):
        return self.full_name.split()[0] if self.full_name else self.email.split("@")[0]

    @property
    def is_locked(self):
        """Check if the account is currently locked."""
        if self.lockout_until and self.lockout_until > timezone.now():
            return True
        return False

    def record_failed_login(self):
        """Record a failed login attempt and lock account if threshold exceeded."""
        self.failed_login_attempts += 1
        
        # Lock account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            # Progressive lockout: 5 min, 15 min, 30 min, 1 hour, etc.
            lockout_minutes = min(5 * (2 ** (self.failed_login_attempts - 5)), 60)
            self.lockout_until = timezone.now() + timedelta(minutes=lockout_minutes)
            logger.warning(
                f"Account locked for {self.email} after {self.failed_login_attempts} "
                f"failed attempts. Locked until {self.lockout_until}"
            )
        
        self.save(update_fields=["failed_login_attempts", "lockout_until"])

    def record_successful_login(self, ip_address=None):
        """Reset failed attempts on successful login."""
        self.failed_login_attempts = 0
        self.lockout_until = None
        self.last_login = timezone.now()
        if ip_address:
            self.last_login_ip = ip_address
        self.save(update_fields=[
            "failed_login_attempts", "lockout_until", "last_login", "last_login_ip"
        ])

    def get_lockout_remaining(self):
        """Get remaining lockout time in minutes."""
        if self.lockout_until and self.lockout_until > timezone.now():
            delta = self.lockout_until - timezone.now()
            return int(delta.total_seconds() / 60) + 1
        return 0


# ==============================================================================
# PASSWORD RESET REQUEST (Admin-Controlled)
# ==============================================================================


class PasswordResetRequest(models.Model):
    """
    Password reset request that requires admin approval.
    
    Users cannot reset their own passwords - they must request
    a reset which an admin will process manually.
    """

    STATUS_CHOICES = [
        ("pending", "Pending Review"),
        ("approved", "Approved - Password Reset"),
        ("rejected", "Rejected"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="password_reset_requests",
    )
    reason = models.TextField(
        help_text="Reason for password reset request.",
        validators=[MinLengthValidator(10)],
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    
    # Security tracking
    request_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
    )
    user_agent = models.TextField(
        blank=True,
        max_length=500,
    )
    
    # Admin processing
    processed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="processed_reset_requests",
        limit_choices_to={"is_staff": True},
    )
    processed_at = models.DateTimeField(
        null=True,
        blank=True,
    )
    admin_notes = models.TextField(
        blank=True,
        help_text="Notes from admin about this request.",
    )
    
    # Temporary password (generated by admin, hashed)
    temp_password_hash = models.CharField(
        max_length=255,
        blank=True,
        help_text="Hashed temporary password set by admin.",
    )
    temp_password_expires = models.DateTimeField(
        null=True,
        blank=True,
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Password Reset Request"
        verbose_name_plural = "Password Reset Requests"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Reset request for {self.user.email} - {self.status}"

    @property
    def is_pending(self):
        return self.status == "pending"

    def approve(self, admin_user, temp_password=None):
        """
        Approve the request and optionally set a temporary password.
        
        Args:
            admin_user: The admin processing the request
            temp_password: Optional temporary password to set
        """
        from django.contrib.auth.hashers import make_password
        
        self.status = "approved"
        self.processed_by = admin_user
        self.processed_at = timezone.now()
        
        if temp_password:
            self.temp_password_hash = make_password(temp_password)
            self.temp_password_expires = timezone.now() + timedelta(hours=24)
            
            # Set the temporary password on the user
            self.user.set_password(temp_password)
            self.user.last_password_change = timezone.now()
            self.user.save(update_fields=["password", "last_password_change"])
            
            logger.info(
                f"Password reset approved for {self.user.email} by {admin_user.email}"
            )
        
        self.save()

    def reject(self, admin_user, reason=""):
        """Reject the password reset request."""
        self.status = "rejected"
        self.processed_by = admin_user
        self.processed_at = timezone.now()
        if reason:
            self.admin_notes = reason
        self.save()
        
        logger.info(
            f"Password reset rejected for {self.user.email} by {admin_user.email}"
        )


# ==============================================================================
# LOGIN HISTORY
# ==============================================================================


class LoginHistory(models.Model):
    """
    Track user login attempts for security auditing.
    """

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="login_history",
        null=True,
        blank=True,
    )
    email_attempted = models.EmailField(
        help_text="Email address used in login attempt.",
    )
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(
        max_length=500,
        blank=True,
    )
    success = models.BooleanField(
        default=False,
    )
    failure_reason = models.CharField(
        max_length=100,
        blank=True,
        choices=[
            ("invalid_credentials", "Invalid Credentials"),
            ("account_locked", "Account Locked"),
            ("account_inactive", "Account Inactive"),
            ("account_unverified", "Account Not Verified"),
        ],
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Login History"
        verbose_name_plural = "Login History"
        ordering = ["-timestamp"]

    def __str__(self):
        status = "Success" if self.success else "Failed"
        return f"{self.email_attempted} - {status} - {self.timestamp}"
