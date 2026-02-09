"""
Test factories for the Contact app models.
"""

import factory
from django.utils import timezone

from apps.contact.models import ContactSubmission


class ContactSubmissionFactory(factory.django.DjangoModelFactory):
    """Factory for creating ContactSubmission instances."""

    class Meta:
        model = ContactSubmission

    name = factory.Sequence(lambda n: f"Test User {n}")
    email = factory.LazyAttribute(lambda obj: f"{obj.name.lower().replace(' ', '.')}@example.com")
    message = factory.Sequence(lambda n: f"This is test message number {n}. It has enough characters to pass validation.")
    created_at = factory.LazyFunction(timezone.now)
    is_read = False
    ip_address = "127.0.0.1"
    user_agent = "TestAgent/1.0"
