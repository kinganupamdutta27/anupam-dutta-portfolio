"""
Tests for Contact app forms.

Tests cover:
    - Valid form submission
    - Field validation (name, email, message)
    - Spam detection (keywords, URLs, honeypot)
    - Rate limiting
"""

import pytest

from apps.contact.forms import ContactForm
from .factories import ContactSubmissionFactory


@pytest.mark.django_db
class TestContactForm:
    """Tests for the ContactForm."""

    def test_valid_form(self):
        """Test a valid form submission."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "message": "Hello, I would like to discuss a project opportunity.",
            "website": "",  # honeypot
        }
        form = ContactForm(data=data)
        assert form.is_valid(), form.errors

    def test_empty_name_invalid(self):
        """Test that empty name is invalid."""
        data = {
            "name": "",
            "email": "john@example.com",
            "message": "A valid message here.",
            "website": "",
        }
        form = ContactForm(data=data)
        assert not form.is_valid()
        assert "name" in form.errors

    def test_short_name_invalid(self):
        """Test that a 1-character name is invalid."""
        data = {
            "name": "J",
            "email": "john@example.com",
            "message": "A valid message here.",
            "website": "",
        }
        form = ContactForm(data=data)
        assert not form.is_valid()
        assert "name" in form.errors

    def test_invalid_email(self):
        """Test that an invalid email is rejected."""
        data = {
            "name": "John Doe",
            "email": "not-an-email",
            "message": "A valid message here.",
            "website": "",
        }
        form = ContactForm(data=data)
        assert not form.is_valid()
        assert "email" in form.errors

    def test_short_message_invalid(self):
        """Test that a message shorter than 10 chars is invalid."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "message": "Short",
            "website": "",
        }
        form = ContactForm(data=data)
        assert not form.is_valid()
        assert "message" in form.errors

    def test_spam_keyword_detected(self):
        """Test that spam keywords are detected."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "message": "Congratulations! You won the lottery! Click here to claim.",
            "website": "",
        }
        form = ContactForm(data=data)
        assert not form.is_valid()
        assert "message" in form.errors

    def test_excessive_urls_detected(self):
        """Test that excessive URLs are detected."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "message": (
                "Check http://one.com and http://two.com "
                "and http://three.com and http://four.com"
            ),
            "website": "",
        }
        form = ContactForm(data=data)
        assert not form.is_valid()
        assert "message" in form.errors

    def test_honeypot_filled_rejects(self):
        """Test that a filled honeypot field rejects the form."""
        data = {
            "name": "John Doe",
            "email": "john@example.com",
            "message": "A valid message here.",
            "website": "spam-bot-filled-this",
        }
        form = ContactForm(data=data)
        assert not form.is_valid()

    def test_special_chars_in_name_rejected(self):
        """Test that special characters in name are rejected."""
        data = {
            "name": "<script>alert('xss')</script>",
            "email": "john@example.com",
            "message": "A valid message here.",
            "website": "",
        }
        form = ContactForm(data=data)
        assert not form.is_valid()
        assert "name" in form.errors

    def test_rate_limit_check_within_limit(self):
        """Test rate limit check when within limit."""
        form = ContactForm()
        assert form.check_rate_limit("127.0.0.1") is True

    def test_rate_limit_check_exceeded(self):
        """Test rate limit check when exceeded."""
        # Create 5 submissions from the same IP
        for _ in range(5):
            ContactSubmissionFactory(ip_address="192.168.1.100")

        form = ContactForm()
        assert form.check_rate_limit("192.168.1.100") is False

    def test_rate_limit_none_ip(self):
        """Test rate limit check with None IP."""
        form = ContactForm()
        assert form.check_rate_limit(None) is True
