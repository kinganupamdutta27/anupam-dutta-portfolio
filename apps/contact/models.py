"""
Contact app models.

Contains:
    - ContactSubmission: Stores contact form submissions with metadata.
"""

import logging

from django.db import models
from django.utils import timezone

logger = logging.getLogger(__name__)


class ContactSubmission(models.Model):
    """
    Stores contact form submissions from website visitors.

    Includes metadata like IP address and user agent for spam tracking.
    Managed through Django admin (Unfold theme).
    """

    name = models.CharField(
        max_length=200,
        help_text="Sender's name.",
    )
    email = models.EmailField(
        help_text="Sender's email address.",
    )
    message = models.TextField(
        help_text="The message content.",
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When the message was submitted.",
    )
    is_read = models.BooleanField(
        default=False,
        db_index=True,
        help_text="Whether the message has been read.",
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Sender's IP address (for spam tracking).",
    )
    user_agent = models.TextField(
        blank=True,
        help_text="Sender's browser user agent string.",
    )

    class Meta:
        verbose_name = "Contact Submission"
        verbose_name_plural = "Contact Submissions"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["-created_at"]),
            models.Index(fields=["is_read", "-created_at"]),
        ]

    def __str__(self):
        return f"{self.name} <{self.email}> - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def mark_as_read(self):
        """Mark this submission as read."""
        if not self.is_read:
            self.is_read = True
            self.save(update_fields=["is_read"])
            logger.info(f"Contact submission {self.pk} marked as read.")

    @classmethod
    def unread_count(cls):
        """Return the count of unread submissions."""
        return cls.objects.filter(is_read=False).count()
