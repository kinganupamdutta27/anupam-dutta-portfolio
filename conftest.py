"""
Global test configuration and fixtures.

Provides shared fixtures for all test modules including
Wagtail page tree setup and common test utilities.
"""

import pytest

from django.test import RequestFactory
from wagtail.models import Page, Site


@pytest.fixture
def request_factory():
    """Provide a Django RequestFactory instance."""
    return RequestFactory()


@pytest.fixture
def rf(request_factory):
    """Alias for request_factory fixture."""
    return request_factory


@pytest.fixture
def wagtail_root_page(db):
    """Return the Wagtail root page."""
    return Page.objects.first()


@pytest.fixture
def default_site(db, wagtail_root_page):
    """Return or create the default Wagtail site."""
    site, created = Site.objects.get_or_create(
        is_default_site=True,
        defaults={
            "hostname": "localhost",
            "port": 80,
            "root_page": wagtail_root_page,
            "site_name": "Test Site",
        },
    )
    return site


@pytest.fixture
def home_page(db, wagtail_root_page):
    """Create and return a HomePage instance."""
    from apps.home.models import HomePage

    # Remove default Wagtail "Welcome" page that conflicts with slug "home"
    existing = Page.objects.filter(slug="home", depth=2)
    if existing.exists():
        existing.delete()
        Page.fix_tree()
        wagtail_root_page = Page.objects.get(pk=wagtail_root_page.pk)

    home = HomePage(
        title="Home",
        slug="home",
        hero_name="Test User",
        hero_greeting="Hi, I'm",
        hero_tag_text="Available for opportunities",
    )
    wagtail_root_page.add_child(instance=home)
    home.save_revision().publish()

    # Ensure default site points to home page
    site, _ = Site.objects.get_or_create(
        is_default_site=True,
        defaults={"hostname": "localhost", "port": 80, "root_page": home},
    )
    if site.root_page != home:
        site.root_page = home
        site.save()

    return home


@pytest.fixture
def sample_request(rf, default_site):
    """Create a sample GET request."""
    request = rf.get("/")
    request.META["SERVER_NAME"] = "localhost"
    request.META["SERVER_PORT"] = "80"
    return request
