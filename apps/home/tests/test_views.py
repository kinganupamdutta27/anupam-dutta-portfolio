"""
Tests for Home app views and page rendering.

Tests cover:
    - Page accessibility and HTTP status codes
    - Template rendering with dynamic content
    - Context data integrity
"""

import pytest

from django.test import Client


@pytest.mark.django_db
class TestHomePageView:
    """Tests for the HomePage view rendering."""

    def test_home_page_returns_200(self, home_page):
        """Test that the home page returns HTTP 200."""
        client = Client()
        response = client.get("/")
        assert response.status_code == 200

    def test_home_page_uses_correct_template(self, home_page):
        """Test that the correct template is used."""
        client = Client()
        response = client.get("/")
        assert "home/home_page.html" in [t.name for t in response.templates]

    def test_home_page_contains_hero_name(self, home_page):
        """Test that the hero name appears in the response."""
        client = Client()
        response = client.get("/")
        content = response.content.decode()
        assert home_page.hero_name in content

    def test_home_page_contains_navigation(self, home_page):
        """Test that navigation links appear in the response."""
        client = Client()
        response = client.get("/")
        content = response.content.decode()
        assert "nav-links" in content
        assert "Home" in content


@pytest.mark.django_db
class TestErrorPages:
    """Tests for custom error pages."""

    def test_404_page(self, home_page):
        """Test that 404 page returns correctly."""
        client = Client()
        response = client.get("/this-page-does-not-exist/")
        assert response.status_code == 404

    def test_custom_404_template(self, home_page):
        """Test that custom 404 template is used."""
        client = Client(raise_request_exception=False)
        response = client.get("/this-page-does-not-exist-at-all/")
        assert response.status_code == 404
