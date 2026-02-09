"""
Tests for Home app models.

Tests cover:
    - Model creation and string representations
    - Field validations and constraints
    - Model properties and methods
    - Page hierarchy and max_count enforcement
    - Context generation for templates
"""

import pytest
from django.core.exceptions import ValidationError

from apps.home.models import (
    AboutStat,
    ContactLink,
    HeroSocialLink,
    HeroTypingText,
    HomePage,
    SiteConfiguration,
)


@pytest.mark.django_db
class TestHomePage:
    """Tests for the HomePage model."""

    def test_create_home_page(self, home_page):
        """Test that a HomePage can be created successfully."""
        assert home_page is not None
        assert home_page.pk is not None
        assert home_page.title == "Home"

    def test_home_page_str(self, home_page):
        """Test HomePage string representation."""
        assert str(home_page) == "Home"

    def test_home_page_default_values(self, home_page):
        """Test that default values are set correctly."""
        assert home_page.hero_greeting == "Hi, I'm"
        assert home_page.hero_tag_text == "Available for opportunities"
        assert home_page.show_about is True
        assert home_page.show_skills is True
        assert home_page.show_projects is True

    def test_home_page_template(self, home_page):
        """Test that the correct template is assigned."""
        assert home_page.template == "home/home_page.html"

    def test_home_page_max_count(self):
        """Test that max_count is set to 1."""
        assert HomePage.max_count == 1

    def test_home_page_context_contains_portfolio_data(self, home_page, sample_request):
        """Test that get_context includes portfolio data keys."""
        context = home_page.get_context(sample_request)
        assert "skill_categories" in context
        assert "experiences" in context
        assert "projects" in context
        assert "educations" in context
        assert "certifications" in context
        assert "nav_sections" in context
        assert "typing_texts_list" in context

    def test_navigation_sections_respects_visibility(self, home_page, sample_request):
        """Test that nav sections respect show_* toggles."""
        home_page.show_about = False
        home_page.save()

        context = home_page.get_context(sample_request)
        nav_anchors = [anchor for anchor, label in context["nav_sections"]]
        assert "about" not in nav_anchors
        assert "home" in nav_anchors

    def test_navigation_sections_all_visible(self, home_page, sample_request):
        """Test all sections visible when all toggles are True."""
        context = home_page.get_context(sample_request)
        nav_anchors = [anchor for anchor, label in context["nav_sections"]]
        assert "home" in nav_anchors
        assert "about" in nav_anchors
        assert "skills" in nav_anchors
        assert "experience" in nav_anchors
        assert "projects" in nav_anchors
        assert "contact" in nav_anchors


@pytest.mark.django_db
class TestHeroTypingText:
    """Tests for the HeroTypingText model."""

    def test_create_typing_text(self, home_page):
        """Test creating a typing text entry."""
        text = HeroTypingText.objects.create(
            page=home_page,
            text="Python Developer",
            sort_order=0,
        )
        assert text.pk is not None
        assert str(text) == "Python Developer"

    def test_typing_text_ordering(self, home_page):
        """Test that typing texts are ordered by sort_order."""
        HeroTypingText.objects.create(page=home_page, text="Second", sort_order=2)
        HeroTypingText.objects.create(page=home_page, text="First", sort_order=1)

        texts = list(home_page.hero_typing_texts.order_by("sort_order"))
        assert texts[0].text == "First"
        assert texts[1].text == "Second"


@pytest.mark.django_db
class TestHeroSocialLink:
    """Tests for the HeroSocialLink model."""

    def test_create_social_link(self, home_page):
        """Test creating a social link."""
        link = HeroSocialLink.objects.create(
            page=home_page,
            platform="linkedin",
            url="https://linkedin.com/in/test",
            icon_class="fab fa-linkedin-in",
            sort_order=0,
        )
        assert link.pk is not None
        assert "LinkedIn" in str(link)

    def test_email_link_validation(self, home_page):
        """Test that email links require mailto: prefix."""
        link = HeroSocialLink(
            page=home_page,
            platform="email",
            url="test@example.com",  # Missing mailto:
            icon_class="fas fa-envelope",
            sort_order=0,
        )
        with pytest.raises(ValidationError):
            link.clean()

    def test_valid_email_link(self, home_page):
        """Test that valid email links pass validation."""
        link = HeroSocialLink(
            page=home_page,
            platform="email",
            url="mailto:test@example.com",
            icon_class="fas fa-envelope",
            sort_order=0,
        )
        link.clean()  # Should not raise


@pytest.mark.django_db
class TestAboutStat:
    """Tests for the AboutStat model."""

    def test_create_stat(self, home_page):
        """Test creating an about stat."""
        stat = AboutStat.objects.create(
            page=home_page,
            number="10+",
            label="Projects",
            sort_order=0,
        )
        assert str(stat) == "10+ Projects"

    def test_stat_display(self, home_page):
        """Test stat string representation."""
        stat = AboutStat(page=home_page, number="2+", label="Years Experience")
        assert str(stat) == "2+ Years Experience"


@pytest.mark.django_db
class TestContactLink:
    """Tests for the ContactLink model."""

    def test_create_contact_link(self, home_page):
        """Test creating a contact link."""
        link = ContactLink.objects.create(
            page=home_page,
            contact_type="email",
            display_text="test@example.com",
            url="mailto:test@example.com",
            icon_class="fas fa-envelope",
            sort_order=0,
        )
        assert link.pk is not None
        assert "Email" in str(link)

    def test_contact_link_types(self, home_page):
        """Test different contact link types."""
        for contact_type, label in ContactLink.CONTACT_TYPE_CHOICES:
            link = ContactLink(
                page=home_page,
                contact_type=contact_type,
                display_text=f"Test {label}",
                url=f"https://example.com/{contact_type}",
                icon_class="fas fa-link",
            )
            assert label in str(link)
