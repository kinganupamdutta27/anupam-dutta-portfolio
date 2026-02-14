"""
Authentication forms with security features.

Includes:
    - Registration form with strong password validation
    - Login form with rate limiting
    - Password change form
    - Password reset request form
    - Profile update form
"""

import re
import logging

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.core.validators import MinLengthValidator

from .models import User, PasswordResetRequest

logger = logging.getLogger(__name__)


# ==============================================================================
# REGISTRATION FORM
# ==============================================================================


class UserRegistrationForm(UserCreationForm):
    """
    User registration form with enhanced security validation.
    """

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "your@email.com",
            "autocomplete": "email",
        }),
    )
    full_name = forms.CharField(
        max_length=255,
        validators=[MinLengthValidator(2)],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "John Doe",
            "autocomplete": "name",
        }),
    )
    company = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Company Name (optional)",
            "autocomplete": "organization",
        }),
    )
    password1 = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Create a strong password",
            "autocomplete": "new-password",
        }),
    )
    password2 = forms.CharField(
        label="Confirm Password",
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm your password",
            "autocomplete": "new-password",
        }),
    )
    
    # Honeypot field for bot detection
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
    )
    
    # Terms acceptance
    accept_terms = forms.BooleanField(
        required=True,
        error_messages={"required": "You must accept the terms and conditions."},
    )

    class Meta:
        model = User
        fields = ["email", "full_name", "company", "password1", "password2"]

    def clean_website(self):
        """Honeypot validation."""
        value = self.cleaned_data.get("website", "")
        if value:
            logger.warning("Registration honeypot triggered - possible bot.")
            raise ValidationError("Bot detected.")
        return value

    def clean_email(self):
        """Validate and normalize email."""
        email = self.cleaned_data.get("email", "").strip().lower()
        
        # Block disposable email domains
        disposable_domains = [
            "mailinator.com", "guerrillamail.com", "tempmail.com",
            "throwaway.email", "10minutemail.com", "temp-mail.org",
        ]
        domain = email.split("@")[-1] if "@" in email else ""
        if domain in disposable_domains:
            raise ValidationError("Please use a valid email address, not a disposable one.")
        
        return email

    def clean_full_name(self):
        """Validate name field."""
        name = self.cleaned_data.get("full_name", "").strip()
        
        # Check for suspicious characters
        if re.search(r"[<>{}[\]\\|`~]", name):
            raise ValidationError("Name contains invalid characters.")
        
        # Check for excessive numbers
        if sum(c.isdigit() for c in name) > 3:
            raise ValidationError("Name cannot contain excessive numbers.")
        
        return name

    def clean_password1(self):
        """Enhanced password validation."""
        password = self.cleaned_data.get("password1", "")
        
        # Django's built-in validators
        validate_password(password)
        
        # Additional custom checks
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one number.")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError("Password must contain at least one special character.")
        
        return password

    def save(self, commit=True):
        """Save user with additional fields."""
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.full_name = self.cleaned_data["full_name"]
        user.company = self.cleaned_data.get("company", "")
        
        if commit:
            user.save()
        
        return user


# ==============================================================================
# LOGIN FORM
# ==============================================================================


class SecureLoginForm(forms.Form):
    """
    Secure login form with account lockout support.
    """

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "your@email.com",
            "autocomplete": "email",
        }),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Your password",
            "autocomplete": "current-password",
        }),
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input",
        }),
    )

    def __init__(self, request=None, *args, **kwargs):
        self.request = request
        self.user_cache = None
        super().__init__(*args, **kwargs)

    def clean(self):
        """Authenticate user with security checks."""
        cleaned_data = super().clean()
        email = cleaned_data.get("email", "").strip().lower()
        password = cleaned_data.get("password", "")

        if email and password:
            # Check if user exists and is locked
            try:
                user = User.objects.get(email=email)
                
                if user.is_locked:
                    remaining = user.get_lockout_remaining()
                    raise ValidationError(
                        f"Account is temporarily locked. Try again in {remaining} minutes."
                    )
                
                if not user.is_active:
                    raise ValidationError("This account has been deactivated.")
                
            except User.DoesNotExist:
                # Don't reveal that user doesn't exist
                pass

            # Attempt authentication
            self.user_cache = authenticate(
                self.request,
                email=email,
                password=password,
            )

            if self.user_cache is None:
                # Record failed attempt if user exists
                try:
                    user = User.objects.get(email=email)
                    user.record_failed_login()
                except User.DoesNotExist:
                    pass
                
                raise ValidationError(
                    "Invalid email or password. Please try again."
                )

        return cleaned_data

    def get_user(self):
        """Return the authenticated user."""
        return self.user_cache


# ==============================================================================
# PASSWORD RESET REQUEST FORM
# ==============================================================================


class PasswordResetRequestForm(forms.ModelForm):
    """
    Form for users to request a password reset (admin-controlled).
    """

    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "your@email.com",
            "autocomplete": "email",
        }),
        help_text="Enter the email address associated with your account.",
    )
    reason = forms.CharField(
        min_length=10,
        max_length=500,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Please explain why you need to reset your password...",
            "rows": 4,
        }),
        help_text="Provide details to help verify your identity.",
    )

    class Meta:
        model = PasswordResetRequest
        fields = ["reason"]

    def __init__(self, *args, **kwargs):
        self.user = None
        super().__init__(*args, **kwargs)

    def clean_email(self):
        """Validate email and find associated user."""
        email = self.cleaned_data.get("email", "").strip().lower()
        
        try:
            self.user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Don't reveal that user doesn't exist
            pass
        
        return email

    def clean(self):
        """Check for existing pending requests."""
        cleaned_data = super().clean()
        
        if self.user:
            # Check for recent pending requests
            recent_request = PasswordResetRequest.objects.filter(
                user=self.user,
                status="pending",
            ).exists()
            
            if recent_request:
                raise ValidationError(
                    "You already have a pending password reset request. "
                    "Please wait for an administrator to process it."
                )
        
        return cleaned_data

    def save(self, commit=True, ip_address=None, user_agent=""):
        """Save the password reset request."""
        if not self.user:
            # Create a dummy save to not reveal user existence
            return None
        
        instance = super().save(commit=False)
        instance.user = self.user
        instance.request_ip = ip_address
        instance.user_agent = user_agent[:500] if user_agent else ""
        
        if commit:
            instance.save()
            logger.info(f"Password reset request created for {self.user.email}")
        
        return instance


# ==============================================================================
# PASSWORD CHANGE FORM
# ==============================================================================


class SecurePasswordChangeForm(forms.Form):
    """
    Form for authenticated users to change their password.
    """

    current_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Current password",
            "autocomplete": "current-password",
        }),
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "New password",
            "autocomplete": "new-password",
        }),
    )
    confirm_password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "class": "form-control",
            "placeholder": "Confirm new password",
            "autocomplete": "new-password",
        }),
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_current_password(self):
        """Verify current password."""
        password = self.cleaned_data.get("current_password", "")
        
        if not self.user.check_password(password):
            raise ValidationError("Current password is incorrect.")
        
        return password

    def clean_new_password(self):
        """Validate new password strength."""
        password = self.cleaned_data.get("new_password", "")
        
        validate_password(password, self.user)
        
        if len(password) < 8:
            raise ValidationError("Password must be at least 8 characters long.")
        
        if not re.search(r"[A-Z]", password):
            raise ValidationError("Password must contain at least one uppercase letter.")
        
        if not re.search(r"[a-z]", password):
            raise ValidationError("Password must contain at least one lowercase letter.")
        
        if not re.search(r"\d", password):
            raise ValidationError("Password must contain at least one number.")
        
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", password):
            raise ValidationError("Password must contain at least one special character.")
        
        return password

    def clean(self):
        """Verify passwords match."""
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")
        
        if new_password and confirm_password:
            if new_password != confirm_password:
                raise ValidationError({"confirm_password": "Passwords do not match."})
        
        return cleaned_data

    def save(self):
        """Update user password."""
        from django.utils import timezone
        
        self.user.set_password(self.cleaned_data["new_password"])
        self.user.last_password_change = timezone.now()
        self.user.save(update_fields=["password", "last_password_change"])
        
        logger.info(f"Password changed for user {self.user.email}")
        return self.user


# ==============================================================================
# PROFILE UPDATE FORM
# ==============================================================================


class ProfileUpdateForm(forms.ModelForm):
    """
    Form for users to update their profile information.
    """

    class Meta:
        model = User
        fields = ["full_name", "phone", "company", "bio", "profile_image"]
        widgets = {
            "full_name": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Your full name",
            }),
            "phone": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "+91 9876543210",
            }),
            "company": forms.TextInput(attrs={
                "class": "form-control",
                "placeholder": "Company name",
            }),
            "bio": forms.Textarea(attrs={
                "class": "form-control",
                "placeholder": "Tell us about yourself...",
                "rows": 4,
            }),
            "profile_image": forms.FileInput(attrs={
                "class": "form-control",
            }),
        }

    def clean_full_name(self):
        """Validate name field."""
        name = self.cleaned_data.get("full_name", "").strip()
        
        if re.search(r"[<>{}[\]\\|`~]", name):
            raise ValidationError("Name contains invalid characters.")
        
        return name

    def clean_phone(self):
        """Validate phone number."""
        phone = self.cleaned_data.get("phone", "").strip()
        
        if phone:
            # Remove common formatting characters
            cleaned = re.sub(r"[\s\-\(\)\.]", "", phone)
            
            # Check if it looks like a valid phone number
            if not re.match(r"^\+?\d{10,15}$", cleaned):
                raise ValidationError("Please enter a valid phone number.")
        
        return phone
