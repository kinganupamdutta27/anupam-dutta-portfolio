"""
Portfolio app models for the Anupam Dutta Portfolio.

Contains Wagtail Snippets for all portfolio content:
    - SkillCategory & Skill: Technical skills grouped by category
    - Experience & ExperienceHighlight: Work experience timeline
    - Project & ProjectTechnology: Featured projects with tech stacks
    - Education: Academic qualifications
    - Certification: Professional certifications

All models support:
    - Wagtail Snippet admin management
    - Active/inactive toggle for soft visibility control
    - Custom ordering via sort_order field
    - Proper validation and clean methods
"""

import logging

from django.core.exceptions import ValidationError
from django.db import models

from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel
from wagtail.admin.panels import FieldPanel, FieldRowPanel, InlinePanel, MultiFieldPanel
from wagtail.models import Orderable
from wagtail.search import index
# Note: Snippet registration is done via custom ViewSets in wagtail_hooks.py
# Do NOT add @register_snippet decorators on these models.

logger = logging.getLogger(__name__)


# ==============================================================================
# SKILL CATEGORY & SKILL
# ==============================================================================


class SkillCategory(ClusterableModel):
    """
    A category of technical skills (e.g., 'Programming Languages', 'Backend Development').

    Each category contains multiple skills as inline orderables.
    """

    name = models.CharField(
        max_length=200,
        help_text="Category name (e.g., 'Programming Languages').",
    )
    icon_class = models.CharField(
        max_length=100,
        help_text="Font Awesome icon class (e.g., 'fas fa-code').",
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this category from the website.",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("icon_class"),
        FieldPanel("sort_order"),
        FieldPanel("is_active"),
        InlinePanel("skills", label="Skills"),
    ]

    search_fields = [
        index.SearchField("name"),
    ]

    class Meta:
        verbose_name = "Skill Category"
        verbose_name_plural = "Skill Categories"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return self.name

    @property
    def skill_count(self):
        """Return the number of skills in this category."""
        return self.skills.count()


class Skill(Orderable):
    """An individual skill within a category."""

    category = ParentalKey(
        SkillCategory,
        on_delete=models.CASCADE,
        related_name="skills",
    )
    name = models.CharField(
        max_length=200,
        help_text="Skill name (e.g., 'Python', 'FastAPI').",
    )

    panels = [FieldPanel("name")]

    class Meta(Orderable.Meta):
        verbose_name = "Skill"
        verbose_name_plural = "Skills"

    def __str__(self):
        return self.name


# ==============================================================================
# EXPERIENCE & HIGHLIGHTS
# ==============================================================================


class Experience(ClusterableModel):
    """
    A work experience entry in the career timeline.

    Each experience can have multiple highlight bullet points
    managed as inline orderables.
    """

    job_title = models.CharField(
        max_length=200,
        help_text="Your job title (e.g., 'Jr. Python Developer').",
    )
    company_name = models.CharField(
        max_length=200,
        help_text="Company name (e.g., 'Weavers Web Solutions').",
    )
    company_url = models.URLField(
        blank=True,
        help_text="Company website URL (optional).",
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        help_text="Work location (e.g., 'Kolkata').",
    )
    start_date = models.DateField(
        help_text="When you started this position.",
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        help_text="When you left (leave blank for current position).",
    )
    is_current = models.BooleanField(
        default=False,
        help_text="Check if this is your current position.",
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Custom ordering (lower numbers first). Default ordering is by start date.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this experience from the website.",
    )

    panels = [
        MultiFieldPanel(
            [
                FieldPanel("job_title"),
                FieldPanel("company_name"),
                FieldPanel("company_url"),
                FieldPanel("location"),
            ],
            heading="Position Details",
        ),
        MultiFieldPanel(
            [
                FieldRowPanel(
                    [
                        FieldPanel("start_date"),
                        FieldPanel("end_date"),
                    ]
                ),
                FieldPanel("is_current"),
            ],
            heading="Duration",
        ),
        FieldPanel("sort_order"),
        FieldPanel("is_active"),
        InlinePanel("highlights", label="Key Achievements / Highlights"),
    ]

    search_fields = [
        index.SearchField("job_title"),
        index.SearchField("company_name"),
        index.SearchField("location"),
    ]

    class Meta:
        verbose_name = "Experience"
        verbose_name_plural = "Experiences"
        ordering = ["-start_date"]

    def __str__(self):
        return f"{self.job_title} at {self.company_name}"

    def clean(self):
        """Validate date ranges and current position logic."""
        super().clean()
        errors = {}

        if self.end_date and self.start_date and self.end_date < self.start_date:
            errors["end_date"] = "End date cannot be before the start date."

        if self.is_current and self.end_date:
            errors["end_date"] = (
                "A current position should not have an end date. "
                "Either uncheck 'Is current' or clear the end date."
            )

        if errors:
            raise ValidationError(errors)

    @property
    def date_range(self):
        """Return a formatted date range string (e.g., 'April 2025 - Present')."""
        try:
            start = self.start_date.strftime("%B %Y")
            if self.is_current:
                return f"{start} - Present"
            if self.end_date:
                return f"{start} - {self.end_date.strftime('%B %Y')}"
            return start
        except (AttributeError, ValueError):
            return ""

    @property
    def company_display(self):
        """Return formatted company and location string."""
        parts = [self.company_name]
        if self.location:
            parts.append(self.location)
        return " \u2022 ".join(parts)


class ExperienceHighlight(Orderable):
    """A bullet-point achievement/highlight for an experience entry."""

    experience = ParentalKey(
        Experience,
        on_delete=models.CASCADE,
        related_name="highlights",
    )
    text = models.TextField(
        help_text="A key achievement or responsibility.",
    )

    panels = [FieldPanel("text")]

    class Meta(Orderable.Meta):
        verbose_name = "Highlight"
        verbose_name_plural = "Highlights"

    def __str__(self):
        return self.text[:80] + ("..." if len(self.text) > 80 else "")


# ==============================================================================
# PROJECT & TECHNOLOGY
# ==============================================================================


class Project(ClusterableModel):
    """
    A portfolio project with description, image, links, and tech stack.

    Technologies are managed as inline orderables.
    """

    title = models.CharField(
        max_length=200,
        help_text="Project title (e.g., 'Plugg - GenAI Matchmaking App').",
    )
    description = models.TextField(
        help_text="Brief project description (1-2 sentences).",
    )
    image = models.ForeignKey(
        "wagtailimages.Image",
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name="+",
        help_text="Project thumbnail/logo image.",
    )
    live_url = models.URLField(
        blank=True,
        help_text="URL to the live project (optional).",
    )
    github_url = models.URLField(
        blank=True,
        help_text="URL to the GitHub repository (optional).",
    )
    is_featured = models.BooleanField(
        default=True,
        help_text="Featured projects appear on the homepage.",
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this project from the website.",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    panels = [
        FieldPanel("title"),
        FieldPanel("description"),
        FieldPanel("image"),
        MultiFieldPanel(
            [
                FieldPanel("live_url"),
                FieldPanel("github_url"),
            ],
            heading="Links",
        ),
        MultiFieldPanel(
            [
                FieldPanel("is_featured"),
                FieldPanel("is_active"),
                FieldPanel("sort_order"),
            ],
            heading="Visibility & Ordering",
        ),
        InlinePanel("technologies", label="Technologies Used"),
    ]

    search_fields = [
        index.SearchField("title"),
        index.SearchField("description"),
    ]

    class Meta:
        verbose_name = "Project"
        verbose_name_plural = "Projects"
        ordering = ["sort_order", "-created_at"]

    def __str__(self):
        return self.title

    @property
    def has_links(self):
        """Check if the project has any external links."""
        return bool(self.live_url or self.github_url)

    @property
    def technology_list(self):
        """Return a list of technology names."""
        return list(self.technologies.values_list("name", flat=True))


class ProjectTechnology(Orderable):
    """A technology/tool used in a project."""

    project = ParentalKey(
        Project,
        on_delete=models.CASCADE,
        related_name="technologies",
    )
    name = models.CharField(
        max_length=100,
        help_text="Technology name (e.g., 'Python', 'FastAPI', 'Docker').",
    )

    panels = [FieldPanel("name")]

    class Meta(Orderable.Meta):
        verbose_name = "Technology"
        verbose_name_plural = "Technologies"

    def __str__(self):
        return self.name


# ==============================================================================
# EDUCATION
# ==============================================================================


class Education(models.Model):
    """An educational qualification entry."""

    degree = models.CharField(
        max_length=200,
        help_text="Degree title (e.g., 'B.Tech in Computer Science & Engineering').",
    )
    institution = models.CharField(
        max_length=200,
        help_text="Institution name (e.g., 'JIS College of Engineering').",
    )
    institution_url = models.URLField(
        blank=True,
        help_text="Institution website URL (optional).",
    )
    start_year = models.PositiveIntegerField(
        help_text="Year of enrollment.",
    )
    end_year = models.PositiveIntegerField(
        help_text="Year of completion.",
    )
    grade = models.CharField(
        max_length=100,
        blank=True,
        help_text="Grade or GPA (e.g., 'GPA: 8.85').",
    )
    description = models.TextField(
        blank=True,
        help_text="Additional details about the education (optional).",
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this entry from the website.",
    )

    panels = [
        FieldPanel("degree"),
        FieldPanel("institution"),
        FieldPanel("institution_url"),
        FieldRowPanel(
            [
                FieldPanel("start_year"),
                FieldPanel("end_year"),
            ]
        ),
        FieldPanel("grade"),
        FieldPanel("description"),
        FieldPanel("sort_order"),
        FieldPanel("is_active"),
    ]

    search_fields = [
        index.SearchField("degree"),
        index.SearchField("institution"),
    ]

    class Meta:
        verbose_name = "Education"
        verbose_name_plural = "Education"
        ordering = ["-start_year"]

    def __str__(self):
        return f"{self.degree} - {self.institution}"

    def clean(self):
        """Validate year ranges."""
        super().clean()
        if self.end_year and self.start_year and self.end_year < self.start_year:
            raise ValidationError(
                {"end_year": "End year cannot be before the start year."}
            )

    @property
    def year_range(self):
        """Return formatted year range string."""
        return f"{self.start_year} - {self.end_year}"


# ==============================================================================
# CERTIFICATION
# ==============================================================================


class Certification(models.Model):
    """A professional certification or achievement."""

    name = models.CharField(
        max_length=200,
        help_text="Certification name (e.g., 'AWS Cloud Foundations').",
    )
    issuer = models.CharField(
        max_length=200,
        help_text="Issuing organization (e.g., 'Amazon Web Services').",
    )
    icon_class = models.CharField(
        max_length=100,
        help_text="Font Awesome icon class (e.g., 'fab fa-aws').",
    )
    credential_url = models.URLField(
        blank=True,
        help_text="URL to verify the credential (optional).",
    )
    credential_id = models.CharField(
        max_length=200,
        blank=True,
        help_text="Credential ID for verification.",
    )
    date_obtained = models.DateField(
        null=True,
        blank=True,
        help_text="Date the certification was obtained.",
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text="Expiry date (leave blank if no expiry).",
    )
    sort_order = models.PositiveIntegerField(
        default=0,
        help_text="Lower numbers appear first.",
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Uncheck to hide this certification from the website.",
    )

    panels = [
        FieldPanel("name"),
        FieldPanel("issuer"),
        FieldPanel("icon_class"),
        FieldPanel("credential_url"),
        FieldPanel("credential_id"),
        FieldRowPanel(
            [
                FieldPanel("date_obtained"),
                FieldPanel("expiry_date"),
            ]
        ),
        FieldPanel("sort_order"),
        FieldPanel("is_active"),
    ]

    search_fields = [
        index.SearchField("name"),
        index.SearchField("issuer"),
    ]

    class Meta:
        verbose_name = "Certification"
        verbose_name_plural = "Certifications"
        ordering = ["sort_order", "name"]

    def __str__(self):
        return f"{self.name} - {self.issuer}"

    @property
    def is_expired(self):
        """Check if the certification has expired."""
        if not self.expiry_date:
            return False
        from django.utils import timezone
        return self.expiry_date < timezone.now().date()
