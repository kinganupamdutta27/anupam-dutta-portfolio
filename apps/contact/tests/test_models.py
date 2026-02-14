"""
Tests for Contact app models.

Tests cover:
    - Model creation and string representation
    - Mark as read functionality
    - Unread count class method
    - Ordering behavior
"""

import pytest

from apps.contact.models import ContactSubmission
from .factories import ContactSubmissionFactory


@pytest.mark.django_db
class TestContactSubmission:
    """Tests for the ContactSubmission model."""

    def test_create_submission(self):
        """Test creating a contact submission."""
        submission = ContactSubmissionFactory(
            name="John Doe",
            email="john@example.com",
        )
        assert submission.pk is not None
        assert "John Doe" in str(submission)
        assert "john@example.com" in str(submission)

    def test_mark_as_read(self):
        """Test marking a submission as read."""
        submission = ContactSubmissionFactory(is_read=False)
        assert submission.is_read is False

        submission.mark_as_read()
        submission.refresh_from_db()
        assert submission.is_read is True

    def test_mark_as_read_idempotent(self):
        """Test that mark_as_read is idempotent."""
        submission = ContactSubmissionFactory(is_read=True)
        submission.mark_as_read()
        submission.refresh_from_db()
        assert submission.is_read is True

    def test_unread_count(self):
        """Test the unread_count class method."""
        ContactSubmissionFactory(is_read=False)
        ContactSubmissionFactory(is_read=False)
        ContactSubmissionFactory(is_read=True)

        assert ContactSubmission.unread_count() == 2

    def test_ordering_newest_first(self):
        """Test that submissions are ordered newest first."""
        old = ContactSubmissionFactory(name="Old")
        new = ContactSubmissionFactory(name="New")

        submissions = list(ContactSubmission.objects.all())
        assert submissions[0].name == "New"

    def test_default_is_read_false(self):
        """Test that new submissions default to unread."""
        submission = ContactSubmissionFactory()
        assert submission.is_read is False
