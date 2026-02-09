"""
Contact form with validation and spam prevention.
"""

import logging
import re

from django import forms
from django.core.validators import MinLengthValidator

from .models import ContactSubmission

logger = logging.getLogger(__name__)

# Common spam keywords to filter
SPAM_KEYWORDS = [
    "viagra", "casino", "lottery", "winner", "congratulations",
    "click here", "buy now", "free money", "earn money",
    "nigerian prince", "inheritance",
]

# Maximum submissions per IP per hour
RATE_LIMIT_PER_HOUR = 5


class ContactForm(forms.ModelForm):
    """
    Contact form with built-in validation and basic spam prevention.

    Validates:
        - Name: minimum 2 characters
        - Email: valid email format
        - Message: minimum 10 characters, no spam content
        - Honeypot field for bot detection
    """

    # Honeypot field (hidden, should remain empty)
    website = forms.CharField(
        required=False,
        widget=forms.HiddenInput(),
        label="",
    )

    name = forms.CharField(
        max_length=200,
        validators=[MinLengthValidator(2, "Name must be at least 2 characters.")],
        widget=forms.TextInput(
            attrs={
                "placeholder": "John Doe",
                "id": "name",
                "autocomplete": "name",
            }
        ),
    )

    email = forms.EmailField(
        widget=forms.EmailInput(
            attrs={
                "placeholder": "john@example.com",
                "id": "email",
                "autocomplete": "email",
            }
        ),
    )

    message = forms.CharField(
        validators=[MinLengthValidator(10, "Message must be at least 10 characters.")],
        widget=forms.Textarea(
            attrs={
                "placeholder": "Hello Anupam, I'd like to discuss...",
                "id": "message",
                "rows": 5,
            }
        ),
    )

    class Meta:
        model = ContactSubmission
        fields = ["name", "email", "message"]

    def clean_website(self):
        """Honeypot validation - if filled, it's likely a bot."""
        value = self.cleaned_data.get("website", "")
        if value:
            logger.warning("Honeypot field triggered - possible bot submission.")
            raise forms.ValidationError("Bot detected.")
        return value

    def clean_name(self):
        """Validate and sanitize the name field."""
        name = self.cleaned_data.get("name", "").strip()
        # Check for excessive special characters
        if re.search(r"[<>{}[\]\\]", name):
            raise forms.ValidationError("Name contains invalid characters.")
        return name

    def clean_email(self):
        """Validate the email field."""
        email = self.cleaned_data.get("email", "").strip().lower()
        # Block disposable email domains
        disposable_domains = ["mailinator.com", "guerrillamail.com", "tempmail.com"]
        domain = email.split("@")[-1] if "@" in email else ""
        if domain in disposable_domains:
            raise forms.ValidationError("Please use a valid email address.")
        return email

    def clean_message(self):
        """Validate message content and check for spam."""
        message = self.cleaned_data.get("message", "").strip()

        # Check for spam keywords
        message_lower = message.lower()
        for keyword in SPAM_KEYWORDS:
            if keyword in message_lower:
                logger.warning(f"Spam keyword detected in contact form: '{keyword}'")
                raise forms.ValidationError(
                    "Your message was flagged as potential spam. "
                    "Please revise and try again."
                )

        # Check for excessive URLs
        url_count = len(re.findall(r"https?://", message))
        if url_count > 3:
            raise forms.ValidationError(
                "Your message contains too many URLs."
            )

        return message

    def check_rate_limit(self, ip_address):
        """
        Check if the IP has exceeded the submission rate limit.

        Args:
            ip_address: The client's IP address.

        Returns:
            bool: True if within limit, False if rate limited.
        """
        if not ip_address:
            return True

        from django.utils import timezone
        from datetime import timedelta

        one_hour_ago = timezone.now() - timedelta(hours=1)
        recent_count = ContactSubmission.objects.filter(
            ip_address=ip_address,
            created_at__gte=one_hour_ago,
        ).count()

        if recent_count >= RATE_LIMIT_PER_HOUR:
            logger.warning(f"Rate limit exceeded for IP: {ip_address}")
            return False
        return True
