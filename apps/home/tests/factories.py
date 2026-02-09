"""
Test factories for the Home app models.

Uses factory_boy for generating test data with sensible defaults.
"""

import factory
from wagtail.models import Page

from apps.home.models import (
    AboutStat,
    ContactLink,
    HeroSocialLink,
    HeroTypingText,
    HomePage,
)


class HomePageFactory(factory.django.DjangoModelFactory):
    """Factory for creating HomePage instances."""

    class Meta:
        model = HomePage

    title = "Home"
    slug = factory.Sequence(lambda n: f"home-{n}")
    hero_name = "Test User"
    hero_greeting = "Hi, I'm"
    hero_tag_text = "Available for opportunities"
    hero_cta_primary_text = "Get in Touch"
    hero_cta_primary_url = "#contact"
    hero_cta_secondary_text = "View Projects"
    hero_cta_secondary_url = "#projects"
    about_section_label = "About Me"
    about_section_title = "Passionate about"
    about_section_title_highlight = "Innovative Solutions"
    about_description = "<p>Test description.</p>"
    contact_email = "test@example.com"
    contact_heading = "Let's work together!"
    contact_description = "Test contact description."

    @classmethod
    def _create(cls, model_class, *args, **kwargs):
        """Create HomePage as child of root page."""
        root = Page.objects.first()
        instance = model_class(**kwargs)
        root.add_child(instance=instance)
        instance.save_revision().publish()
        return instance


class HeroTypingTextFactory(factory.django.DjangoModelFactory):
    """Factory for creating HeroTypingText instances."""

    class Meta:
        model = HeroTypingText

    page = factory.SubFactory(HomePageFactory)
    text = factory.Sequence(lambda n: f"Typing Text {n}")
    sort_order = factory.Sequence(lambda n: n)


class HeroSocialLinkFactory(factory.django.DjangoModelFactory):
    """Factory for creating HeroSocialLink instances."""

    class Meta:
        model = HeroSocialLink

    page = factory.SubFactory(HomePageFactory)
    platform = "github"
    url = "https://github.com/testuser"
    icon_class = "fab fa-github"
    title = "GitHub"
    sort_order = factory.Sequence(lambda n: n)


class AboutStatFactory(factory.django.DjangoModelFactory):
    """Factory for creating AboutStat instances."""

    class Meta:
        model = AboutStat

    page = factory.SubFactory(HomePageFactory)
    number = "5+"
    label = "Test Metric"
    sort_order = factory.Sequence(lambda n: n)


class ContactLinkFactory(factory.django.DjangoModelFactory):
    """Factory for creating ContactLink instances."""

    class Meta:
        model = ContactLink

    page = factory.SubFactory(HomePageFactory)
    contact_type = "email"
    display_text = "test@example.com"
    url = "mailto:test@example.com"
    icon_class = "fas fa-envelope"
    sort_order = factory.Sequence(lambda n: n)
