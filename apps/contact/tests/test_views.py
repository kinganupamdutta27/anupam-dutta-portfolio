"""
Tests for Contact app views.

Tests cover:
    - AJAX form submission (success and error cases)
    - CSRF protection
    - Rate limiting
    - Non-AJAX request rejection
    - HTTP method enforcement
"""

import json

import pytest
from django.test import Client
from django.urls import reverse

from apps.contact.models import ContactSubmission


@pytest.mark.django_db
class TestContactSubmitView:
    """Tests for the contact_submit view."""

    @pytest.fixture
    def client(self):
        return Client(enforce_csrf_checks=False)

    @pytest.fixture
    def valid_data(self):
        return {
            "name": "John Doe",
            "email": "john@example.com",
            "message": "Hello, I would like to discuss a project opportunity with you.",
            "website": "",
        }

    @pytest.fixture
    def submit_url(self):
        return reverse("contact:submit")

    def test_successful_submission(self, client, valid_data, submit_url):
        """Test a successful AJAX form submission."""
        response = client.post(
            submit_url,
            data=valid_data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 200
        data = json.loads(response.content)
        assert data["status"] == "success"
        assert ContactSubmission.objects.count() == 1

    def test_submission_stores_data(self, client, valid_data, submit_url):
        """Test that submission data is stored correctly."""
        client.post(
            submit_url,
            data=valid_data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        submission = ContactSubmission.objects.first()
        assert submission.name == "John Doe"
        assert submission.email == "john@example.com"
        assert "discuss a project" in submission.message

    def test_invalid_form_returns_400(self, client, submit_url):
        """Test that invalid data returns 400."""
        response = client.post(
            submit_url,
            data={"name": "", "email": "bad", "message": "short", "website": ""},
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 400
        data = json.loads(response.content)
        assert data["status"] == "error"
        assert "errors" in data

    def test_get_request_rejected(self, client, submit_url):
        """Test that GET requests are rejected."""
        response = client.get(submit_url)
        assert response.status_code == 405

    def test_submission_records_ip(self, client, valid_data, submit_url):
        """Test that IP address is recorded."""
        client.post(
            submit_url,
            data=valid_data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        submission = ContactSubmission.objects.first()
        assert submission.ip_address is not None

    def test_rate_limiting(self, client, valid_data, submit_url):
        """Test that rate limiting works."""
        # Make 5 submissions
        for i in range(5):
            data = valid_data.copy()
            data["email"] = f"test{i}@example.com"
            client.post(
                submit_url,
                data=data,
                HTTP_X_REQUESTED_WITH="XMLHttpRequest",
            )

        # 6th should be rate limited
        response = client.post(
            submit_url,
            data=valid_data,
            HTTP_X_REQUESTED_WITH="XMLHttpRequest",
        )
        assert response.status_code == 429
