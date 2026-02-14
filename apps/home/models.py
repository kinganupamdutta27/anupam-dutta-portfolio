"""
Home app models for the Anupam Dutta Portfolio.

Contains:
    - SiteConfiguration: Global site settings (Wagtail Site Settings)
    - HomePage: The main portfolio landing page (Wagtail Page)
    - HeroTypingText: Rotating text items in the hero section (Orderable)
    - HeroSocialLink: Social media links in the hero section (Orderable)
    - AboutStat: Statistics displayed in the about section (Orderable)
    - ContactLink: Contact information links (Orderable)
    - NavigationItem: Configurable navigation menu items (Orderable)
"""

import logging

from django.core.exceptions import ValidationError
from django.db import models

from modelcluster.fields import ParentalKey
from wagtail.admin.panels import (
    FieldPanel,
    FieldRowPanel,
    InlinePanel,
    MultiFieldPanel,
    TabbedInterface,
    ObjectList,
)
from wagtail.contrib.settings.models import BaseSiteSetting, register_setting
from wagtail.fields import RichTextField
from wagtail.models import Orderable, Page

logger = logging.getLogger(__name__)


# ==============================================================================
# SITE CONFIGURATION (Global Settings)
# ==============================================================================


@register_setting(icon="cog")
class SiteConfiguration(BaseSiteSetting):
    """
    Global site configuration managed through Wagtail Settings.

    Accessible in templates via {% load wagtailsettings_tags %}
    and {{ settings.home.SiteConfiguration }}.
    """

    site_name = models.CharField(
        max_length=255,
        default="Anupam Dutta",
        help_text="The site name displayed in the browser tab and SEO.",
    )
    site_tagline = models.CharField(
        max_length=500,
        blank=True,
        default="Python Backend Engineer & GenAI Specialist",
    )
    logo = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Site logo displayed in the navigation.",
    )
    favicon = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Favicon for the browser tab.",
    )
    meta_description = models.TextField(
        max_length=500,
        blank=True,
        default=(
            "Anupam Dutta - Python Backend Engineer & Generative AI Specialist. "
            "Expert in FastAPI, LangChain, LangGraph, and scalable backend development."
        ),
    )
    meta_keywords = models.CharField(
        max_length=500,
        blank=True,
        default="Python Developer, Backend Engineer, GenAI, LLM Engineer, FastAPI, LangChain",
    )
    google_analytics_id = models.CharField(
        max_length=50,
        blank=True,
        help_text="Google Analytics measurement ID (e.g., G-XXXXXXXXXX).",
    )
    footer_text = models.CharField(
        max_length=500,
        blank=True,
        default="Anupam Dutta. All Rights Reserved.",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("site_name"),
                FieldPanel("site_tagline"),
                FieldPanel("logo"),
                FieldPanel("favicon"),
            ],
            heading="Site Identity",
        ),
        MultiFieldPanel(
            [
                FieldPanel("meta_description"),
                FieldPanel("meta_keywords"),
                FieldPanel("google_analytics_id"),
            ],
            heading="SEO & Analytics",
        ),
        FieldPanel("footer_text"),
    ]

    class Meta:
        verbose_name = "Site Configuration"

    def __str__(self):
        return self.site_name


# ==============================================================================
# HOME PAGE
# ==============================================================================


class HomePage(Page):
    """
    The main portfolio landing page.

    This is a single-instance page that aggregates all portfolio sections.
    Content from Portfolio app snippets (Skills, Experience, Projects, etc.)
    is pulled in via the get_context method.

    Sections can be toggled on/off via the Settings tab.
    Section headers (labels, titles) are configurable from the Content tab.
    """

    # ---- Hero Section ----
    hero_tag_text = models.CharField(
        max_length=200,
        default="Available for opportunities",
        help_text="Small tag text above the main heading (e.g., 'Available for opportunities').",
    )
    hero_greeting = models.CharField(
        max_length=200,
        default="Hi, I'm",
        help_text="Text displayed before your name.",
    )
    hero_name = models.CharField(
        max_length=200,
        default="Anupam Dutta",
        help_text="Your name displayed in the hero with gradient styling.",
    )
    hero_cta_primary_text = models.CharField(
        max_length=100,
        default="Get in Touch",
        help_text="Primary call-to-action button text.",
    )
    hero_cta_primary_url = models.CharField(
        max_length=500,
        default="#contact",
        help_text="URL or anchor for the primary CTA (e.g., '#contact').",
    )
    hero_cta_primary_icon = models.CharField(
        max_length=100,
        default="fas fa-paper-plane",
        blank=True,
        help_text="Font Awesome icon class for primary CTA.",
    )
    hero_cta_secondary_text = models.CharField(
        max_length=100,
        default="View Projects",
        help_text="Secondary call-to-action button text.",
    )
    hero_cta_secondary_url = models.CharField(
        max_length=500,
        default="#projects",
        help_text="URL or anchor for the secondary CTA.",
    )
    hero_cta_secondary_icon = models.CharField(
        max_length=100,
        default="fas fa-code",
        blank=True,
        help_text="Font Awesome icon class for secondary CTA.",
    )

    # ---- About Section ----
    about_section_label = models.CharField(max_length=100, default="About Me")
    about_section_title = models.CharField(max_length=200, default="Passionate about")
    about_section_title_highlight = models.CharField(
        max_length=200,
        default="Innovative Solutions",
        help_text="The gradient-highlighted part of the section title.",
    )
    about_image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Profile image for the About section.",
    )
    about_description = RichTextField(
        blank=True,
        help_text="Rich text description for the About section.",
    )

    # ---- Skills Section ----
    skills_section_label = models.CharField(max_length=100, default="Technical Expertise")
    skills_section_title = models.CharField(max_length=200, default="My")
    skills_section_title_highlight = models.CharField(max_length=200, default="Skills")

    # ---- Experience Section ----
    experience_section_label = models.CharField(max_length=100, default="Career Path")
    experience_section_title = models.CharField(max_length=200, default="Work")
    experience_section_title_highlight = models.CharField(max_length=200, default="Experience")

    # ---- Projects Section ----
    projects_section_label = models.CharField(max_length=100, default="Portfolio")
    projects_section_title = models.CharField(max_length=200, default="Featured")
    projects_section_title_highlight = models.CharField(max_length=200, default="Projects")

    # ---- Education Section ----
    education_section_label = models.CharField(max_length=100, default="Academic Background")
    education_section_title = models.CharField(max_length=200, default="My")
    education_section_title_highlight = models.CharField(max_length=200, default="Education")

    # ---- Certifications Section ----
    certifications_section_label = models.CharField(max_length=100, default="Achievements")
    certifications_section_title = models.CharField(max_length=200, default="My")
    certifications_section_title_highlight = models.CharField(max_length=200, default="Certifications")

    # ---- Contact Section ----
    contact_section_label = models.CharField(max_length=100, default="Get in Touch")
    contact_section_title = models.CharField(max_length=200, default="Let's")
    contact_section_title_highlight = models.CharField(max_length=200, default="Connect")
    contact_heading = models.CharField(
        max_length=200,
        default="Let's work together!",
        help_text="Heading text in the contact info area.",
    )
    contact_description = models.TextField(
        blank=True,
        default=(
            "I'm always interested in hearing about new projects and opportunities. "
            "Whether you have a question or just want to say hi, feel free to reach out!"
        ),
    )
    contact_email = models.EmailField(
        blank=True,
        default="anupamdutta27121998.in@gmail.com",
        help_text="Email address for contact form submissions.",
    )

    # ---- Section Visibility Toggles ----
    show_about = models.BooleanField(default=True, verbose_name="Show About Section")
    show_skills = models.BooleanField(default=True, verbose_name="Show Skills Section")
    show_experience = models.BooleanField(default=True, verbose_name="Show Experience Section")
    show_projects = models.BooleanField(default=True, verbose_name="Show Projects Section")
    show_education = models.BooleanField(default=True, verbose_name="Show Education Section")
    show_certifications = models.BooleanField(default=True, verbose_name="Show Certifications Section")
    show_contact = models.BooleanField(default=True, verbose_name="Show Contact Section")

    # ---- Wagtail Admin Panels ----
    content_panels = Page.content_panels + [
        MultiFieldPanel(
            [
                FieldPanel("hero_greeting"),
                FieldPanel("hero_name"),
                FieldPanel("hero_tag_text"),
                FieldRowPanel(
                    [
                        FieldPanel("hero_cta_primary_text"),
                        FieldPanel("hero_cta_primary_url"),
                        FieldPanel("hero_cta_primary_icon"),
                    ]
                ),
                FieldRowPanel(
                    [
                        FieldPanel("hero_cta_secondary_text"),
                        FieldPanel("hero_cta_secondary_url"),
                        FieldPanel("hero_cta_secondary_icon"),
                    ]
                ),
                InlinePanel("hero_typing_texts", label="Typing Texts", min_num=1, max_num=10),
                InlinePanel("hero_social_links", label="Social Links", max_num=10),
            ],
            heading="Hero Section",
            classname="collapsible",
        ),
        MultiFieldPanel(
            [
                FieldPanel("about_section_label"),
                FieldPanel("about_section_title"),
                FieldPanel("about_section_title_highlight"),
                FieldPanel("about_image"),
                FieldPanel("about_description"),
                InlinePanel("about_stats", label="Statistics", max_num=6),
            ],
            heading="About Section",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("skills_section_label"),
                FieldPanel("skills_section_title"),
                FieldPanel("skills_section_title_highlight"),
            ],
            heading="Skills Section Headers",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("experience_section_label"),
                FieldPanel("experience_section_title"),
                FieldPanel("experience_section_title_highlight"),
            ],
            heading="Experience Section Headers",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("projects_section_label"),
                FieldPanel("projects_section_title"),
                FieldPanel("projects_section_title_highlight"),
            ],
            heading="Projects Section Headers",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("education_section_label"),
                FieldPanel("education_section_title"),
                FieldPanel("education_section_title_highlight"),
            ],
            heading="Education Section Headers",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("certifications_section_label"),
                FieldPanel("certifications_section_title"),
                FieldPanel("certifications_section_title_highlight"),
            ],
            heading="Certifications Section Headers",
            classname="collapsible collapsed",
        ),
        MultiFieldPanel(
            [
                FieldPanel("contact_section_label"),
                FieldPanel("contact_section_title"),
                FieldPanel("contact_section_title_highlight"),
                FieldPanel("contact_heading"),
                FieldPanel("contact_description"),
                FieldPanel("contact_email"),
                InlinePanel("contact_links", label="Contact Links", max_num=10),
            ],
            heading="Contact Section",
            classname="collapsible collapsed",
        ),
    ]

    settings_panels = Page.settings_panels + [
        MultiFieldPanel(
            [
                FieldPanel("show_about"),
                FieldPanel("show_skills"),
                FieldPanel("show_experience"),
                FieldPanel("show_projects"),
                FieldPanel("show_education"),
                FieldPanel("show_certifications"),
                FieldPanel("show_contact"),
            ],
            heading="Section Visibility",
        ),
    ]

    # Use tabbed interface for better organization
    edit_handler = TabbedInterface(
        [
            ObjectList(content_panels, heading="Content"),
            ObjectList(Page.promote_panels, heading="SEO & Promote"),
            ObjectList(settings_panels, heading="Settings"),
        ]
    )

    # ---- Page Configuration ----
    template = "home/home_page.html"
    max_count = 1  # Only one homepage allowed
    parent_page_types = ["wagtailcore.Page"]
    subpage_types = ["blog.BlogIndexPage"]

    class Meta:
        verbose_name = "Home Page"

    def __str__(self):
        return self.title

    def get_context(self, request, *args, **kwargs):
        """
        Enrich template context with portfolio data from snippets.

        Fetches all active Skills, Experiences, Projects, Education,
        and Certifications using optimized queries with prefetch_related.
        All database errors are gracefully handled with empty querysets.
        """
        context = super().get_context(request, *args, **kwargs)

        try:
            from apps.portfolio.models import (
                Certification,
                Education,
                Experience,
                Project,
                SkillCategory,
            )

            context["skill_categories"] = (
                SkillCategory.objects.filter(is_active=True)
                .prefetch_related("skills")
                .order_by("sort_order")
            )
            context["experiences"] = (
                Experience.objects.filter(is_active=True)
                .prefetch_related("highlights")
                .order_by("-start_date")
            )
            context["projects"] = (
                Project.objects.filter(is_active=True, is_featured=True)
                .prefetch_related("technologies")
                .order_by("sort_order")
            )
            context["educations"] = (
                Education.objects.filter(is_active=True).order_by("-start_year")
            )
            context["certifications"] = (
                Certification.objects.filter(is_active=True).order_by("sort_order")
            )

        except Exception as e:
            logger.error(f"Error loading portfolio data: {e}", exc_info=True)
            # Provide empty lists so templates don't break
            context.setdefault("skill_categories", [])
            context.setdefault("experiences", [])
            context.setdefault("projects", [])
            context.setdefault("educations", [])
            context.setdefault("certifications", [])

        # Build navigation items from visible sections
        context["nav_sections"] = self._get_navigation_sections()

        # Typing texts as list for JavaScript
        context["typing_texts_list"] = list(
            self.hero_typing_texts.values_list("text", flat=True)
        )

        return context

    def _get_navigation_sections(self):
        """Build navigation items based on visible sections."""
        sections = [("home", "Home")]

        section_map = [
            (self.show_about, "about", "About"),
            (self.show_skills, "skills", "Skills"),
            (self.show_experience, "experience", "Experience"),
            (self.show_projects, "projects", "Projects"),
            (self.show_contact, "contact", "Contact"),
        ]

        for visible, anchor, label in section_map:
            if visible:
                sections.append((anchor, label))

        return sections


# ==============================================================================
# ORDERABLE MODELS (Inline content for HomePage)
# ==============================================================================


class HeroTypingText(Orderable):
    """Rotating text items displayed with typing animation in the hero."""

    page = ParentalKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name="hero_typing_texts",
    )
    text = models.CharField(
        max_length=200,
        help_text="Text to display in the typing animation (e.g., 'Python Backend Engineer').",
    )

    panels = [FieldPanel("text")]

    class Meta(Orderable.Meta):
        verbose_name = "Typing Text"
        verbose_name_plural = "Typing Texts"

    def __str__(self):
        return self.text


class HeroSocialLink(Orderable):
    """Social media links displayed in the hero section."""

    PLATFORM_CHOICES = [
        ("linkedin", "LinkedIn"),
        ("github", "GitHub"),
        ("twitter", "Twitter/X"),
        ("email", "Email"),
        ("website", "Website"),
        ("youtube", "YouTube"),
        ("instagram", "Instagram"),
        ("stackoverflow", "Stack Overflow"),
        ("medium", "Medium"),
        ("other", "Other"),
    ]

    page = ParentalKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name="hero_social_links",
    )
    platform = models.CharField(
        max_length=50,
        choices=PLATFORM_CHOICES,
        help_text="Social media platform.",
    )
    url = models.CharField(
        max_length=500,
        help_text="Full URL or mailto: link.",
    )
    icon_class = models.CharField(
        max_length=100,
        help_text="Font Awesome icon class (e.g., 'fab fa-linkedin-in').",
    )
    title = models.CharField(
        max_length=100,
        blank=True,
        help_text="Tooltip text on hover.",
    )

    panels = [
        FieldPanel("platform"),
        FieldPanel("url"),
        FieldPanel("icon_class"),
        FieldPanel("title"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = "Social Link"
        verbose_name_plural = "Social Links"

    def __str__(self):
        return f"{self.get_platform_display()} - {self.url}"

    def clean(self):
        super().clean()
        if self.platform == "email" and not self.url.startswith("mailto:"):
            raise ValidationError(
                {"url": "Email links should start with 'mailto:'."}
            )


class AboutStat(Orderable):
    """Statistics displayed in the About section (e.g., '2+ Years Experience')."""

    page = ParentalKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name="about_stats",
    )
    number = models.CharField(
        max_length=20,
        help_text="The statistic value (e.g., '2+', '10+', '6+').",
    )
    label = models.CharField(
        max_length=100,
        help_text="Description of the statistic (e.g., 'Years Experience').",
    )

    panels = [
        FieldPanel("number"),
        FieldPanel("label"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = "About Statistic"
        verbose_name_plural = "About Statistics"

    def __str__(self):
        return f"{self.number} {self.label}"


class ContactLink(Orderable):
    """Contact information links displayed in the Contact section."""

    CONTACT_TYPE_CHOICES = [
        ("email", "Email"),
        ("phone", "Phone"),
        ("linkedin", "LinkedIn"),
        ("github", "GitHub"),
        ("twitter", "Twitter/X"),
        ("website", "Website"),
        ("other", "Other"),
    ]

    page = ParentalKey(
        HomePage,
        on_delete=models.CASCADE,
        related_name="contact_links",
    )
    contact_type = models.CharField(
        max_length=50,
        choices=CONTACT_TYPE_CHOICES,
    )
    display_text = models.CharField(
        max_length=200,
        help_text="Text displayed for this contact method.",
    )
    url = models.CharField(
        max_length=500,
        help_text="Full URL, mailto:, or tel: link.",
    )
    icon_class = models.CharField(
        max_length=100,
        help_text="Font Awesome icon class (e.g., 'fas fa-envelope').",
    )

    panels = [
        FieldPanel("contact_type"),
        FieldPanel("display_text"),
        FieldPanel("url"),
        FieldPanel("icon_class"),
    ]

    class Meta(Orderable.Meta):
        verbose_name = "Contact Link"
        verbose_name_plural = "Contact Links"

    def __str__(self):
        return f"{self.get_contact_type_display()}: {self.display_text}"
