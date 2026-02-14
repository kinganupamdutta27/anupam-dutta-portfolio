"""
Job posting models.

Users can post job opportunities which are saved to the database
and reviewed by admins through the CMS panel.
"""

import logging

from django.conf import settings
from django.core.validators import MinLengthValidator, MinValueValidator
from django.db import models
from django.utils import timezone
from django.utils.text import slugify

logger = logging.getLogger(__name__)


# ==============================================================================
# JOB POST MODEL
# ==============================================================================


class JobPost(models.Model):
    """
    Job posting submitted by authenticated users.
    
    Jobs are submitted by users and reviewed by admins before being
    visible (if a public listing feature is added later).
    """

    STATUS_CHOICES = [
        ("draft", "Draft"),
        ("pending", "Pending Review"),
        ("approved", "Approved"),
        ("rejected", "Rejected"),
        ("closed", "Closed"),
    ]

    JOB_TYPE_CHOICES = [
        ("full_time", "Full Time"),
        ("part_time", "Part Time"),
        ("contract", "Contract"),
        ("freelance", "Freelance"),
        ("internship", "Internship"),
        ("remote", "Remote"),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ("entry", "Entry Level"),
        ("junior", "Junior (1-2 years)"),
        ("mid", "Mid Level (3-5 years)"),
        ("senior", "Senior (5+ years)"),
        ("lead", "Lead / Principal"),
        ("executive", "Executive"),
    ]

    # Basic Information
    title = models.CharField(
        max_length=200,
        validators=[MinLengthValidator(5)],
        help_text="Job title (e.g., 'Senior Python Developer').",
    )
    slug = models.SlugField(
        max_length=250,
        unique=True,
        blank=True,
    )
    company_name = models.CharField(
        max_length=200,
        help_text="Company or organization name.",
    )
    company_website = models.URLField(
        blank=True,
        help_text="Company website URL (optional).",
    )
    company_logo = models.ImageField(
        upload_to="jobs/logos/",
        blank=True,
        null=True,
        help_text="Company logo (optional).",
    )

    # Job Details
    description = models.TextField(
        validators=[MinLengthValidator(50)],
        help_text="Detailed job description.",
    )
    requirements = models.TextField(
        validators=[MinLengthValidator(20)],
        help_text="Job requirements and qualifications.",
    )
    responsibilities = models.TextField(
        blank=True,
        help_text="Key responsibilities (optional).",
    )
    benefits = models.TextField(
        blank=True,
        help_text="Benefits and perks (optional).",
    )

    # Job Classification
    job_type = models.CharField(
        max_length=20,
        choices=JOB_TYPE_CHOICES,
        default="full_time",
    )
    experience_level = models.CharField(
        max_length=20,
        choices=EXPERIENCE_LEVEL_CHOICES,
        default="mid",
    )
    location = models.CharField(
        max_length=200,
        help_text="Job location (e.g., 'Kolkata, India' or 'Remote').",
    )
    is_remote = models.BooleanField(
        default=False,
        help_text="Is this a remote position?",
    )

    # Compensation
    salary_min = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Minimum salary (optional).",
    )
    salary_max = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0)],
        help_text="Maximum salary (optional).",
    )
    salary_currency = models.CharField(
        max_length=10,
        default="INR",
        help_text="Currency code (e.g., INR, USD).",
    )
    show_salary = models.BooleanField(
        default=False,
        help_text="Display salary range publicly?",
    )

    # Contact Information
    contact_email = models.EmailField(
        help_text="Email for applications.",
    )
    contact_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone (optional).",
    )
    application_url = models.URLField(
        blank=True,
        help_text="External application URL (optional).",
    )

    # Skills/Tags
    skills_required = models.TextField(
        blank=True,
        help_text="Comma-separated list of required skills.",
    )

    # Status & Moderation
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending",
    )
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection (if applicable).",
    )
    reviewed_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="reviewed_jobs",
        limit_choices_to={"is_staff": True},
    )
    reviewed_at = models.DateTimeField(
        null=True,
        blank=True,
    )

    # Ownership
    posted_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="job_posts",
    )

    # Validity
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this job posting expires.",
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Job Post"
        verbose_name_plural = "Job Posts"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} at {self.company_name}"

    def save(self, *args, **kwargs):
        """Generate slug if not provided."""
        if not self.slug:
            base_slug = slugify(f"{self.title}-{self.company_name}")
            slug = base_slug
            counter = 1
            while JobPost.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        """Check if the job posting has expired."""
        if self.expires_at:
            return self.expires_at < timezone.now()
        return False

    @property
    def is_active(self):
        """Check if the job is active and visible."""
        return self.status == "approved" and not self.is_expired

    @property
    def salary_range(self):
        """Return formatted salary range."""
        if not self.show_salary:
            return "Not disclosed"
        
        if self.salary_min and self.salary_max:
            return f"{self.salary_currency} {self.salary_min:,.0f} - {self.salary_max:,.0f}"
        elif self.salary_min:
            return f"{self.salary_currency} {self.salary_min:,.0f}+"
        elif self.salary_max:
            return f"Up to {self.salary_currency} {self.salary_max:,.0f}"
        return "Not disclosed"

    @property
    def skills_list(self):
        """Return skills as a list."""
        if not self.skills_required:
            return []
        return [s.strip() for s in self.skills_required.split(",") if s.strip()]

    def approve(self, admin_user):
        """Approve the job posting."""
        self.status = "approved"
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        self.save(update_fields=["status", "reviewed_by", "reviewed_at"])
        logger.info(f"Job post '{self.title}' approved by {admin_user.email}")

    def reject(self, admin_user, reason=""):
        """Reject the job posting."""
        self.status = "rejected"
        self.reviewed_by = admin_user
        self.reviewed_at = timezone.now()
        if reason:
            self.rejection_reason = reason
        self.save(update_fields=["status", "reviewed_by", "reviewed_at", "rejection_reason"])
        logger.info(f"Job post '{self.title}' rejected by {admin_user.email}")

    def close(self):
        """Close the job posting."""
        self.status = "closed"
        self.save(update_fields=["status"])
