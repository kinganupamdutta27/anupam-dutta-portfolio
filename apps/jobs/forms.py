"""
Job posting forms with validation.
"""

import re
import logging

from django import forms
from django.core.validators import MinLengthValidator

from .models import JobPost

logger = logging.getLogger(__name__)


class JobPostForm(forms.ModelForm):
    """
    Form for creating and editing job posts.
    """

    title = forms.CharField(
        max_length=200,
        validators=[MinLengthValidator(5)],
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g., Senior Python Developer",
        }),
    )
    company_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Your company name",
        }),
    )
    company_website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            "class": "form-control",
            "placeholder": "https://yourcompany.com",
        }),
    )
    description = forms.CharField(
        validators=[MinLengthValidator(50)],
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Describe the role, team, and what makes this opportunity exciting...",
            "rows": 6,
        }),
    )
    requirements = forms.CharField(
        validators=[MinLengthValidator(20)],
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "List the required qualifications, skills, and experience...",
            "rows": 4,
        }),
    )
    responsibilities = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Key responsibilities and duties (optional)...",
            "rows": 4,
        }),
    )
    benefits = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            "class": "form-control",
            "placeholder": "Benefits, perks, and what you offer (optional)...",
            "rows": 3,
        }),
    )
    job_type = forms.ChoiceField(
        choices=JobPost.JOB_TYPE_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
        }),
    )
    experience_level = forms.ChoiceField(
        choices=JobPost.EXPERIENCE_LEVEL_CHOICES,
        widget=forms.Select(attrs={
            "class": "form-control",
        }),
    )
    location = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "e.g., Kolkata, India or Remote",
        }),
    )
    is_remote = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input",
        }),
    )
    salary_min = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Minimum salary",
        }),
    )
    salary_max = forms.DecimalField(
        required=False,
        min_value=0,
        widget=forms.NumberInput(attrs={
            "class": "form-control",
            "placeholder": "Maximum salary",
        }),
    )
    salary_currency = forms.CharField(
        max_length=10,
        initial="INR",
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "INR",
        }),
    )
    show_salary = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            "class": "form-check-input",
        }),
    )
    contact_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            "class": "form-control",
            "placeholder": "hr@yourcompany.com",
        }),
    )
    contact_phone = forms.CharField(
        required=False,
        max_length=20,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "+91 9876543210",
        }),
    )
    application_url = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            "class": "form-control",
            "placeholder": "https://yourcompany.com/careers/apply",
        }),
    )
    skills_required = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            "class": "form-control",
            "placeholder": "Python, Django, PostgreSQL, Docker (comma-separated)",
        }),
    )
    company_logo = forms.ImageField(
        required=False,
        widget=forms.FileInput(attrs={
            "class": "form-control",
        }),
    )

    class Meta:
        model = JobPost
        fields = [
            "title",
            "company_name",
            "company_website",
            "company_logo",
            "description",
            "requirements",
            "responsibilities",
            "benefits",
            "job_type",
            "experience_level",
            "location",
            "is_remote",
            "salary_min",
            "salary_max",
            "salary_currency",
            "show_salary",
            "contact_email",
            "contact_phone",
            "application_url",
            "skills_required",
        ]

    def clean_title(self):
        """Validate job title."""
        title = self.cleaned_data.get("title", "").strip()
        
        # Check for suspicious characters
        if re.search(r"[<>{}[\]\\|`~]", title):
            raise forms.ValidationError("Title contains invalid characters.")
        
        return title

    def clean_description(self):
        """Validate description."""
        description = self.cleaned_data.get("description", "").strip()
        
        # Check for spam keywords
        spam_keywords = ["click here", "buy now", "free money", "earn money"]
        description_lower = description.lower()
        
        for keyword in spam_keywords:
            if keyword in description_lower:
                raise forms.ValidationError(
                    "Description contains prohibited content."
                )
        
        return description

    def clean(self):
        """Cross-field validation."""
        cleaned_data = super().clean()
        
        salary_min = cleaned_data.get("salary_min")
        salary_max = cleaned_data.get("salary_max")
        
        if salary_min and salary_max:
            if salary_min > salary_max:
                raise forms.ValidationError({
                    "salary_max": "Maximum salary must be greater than minimum salary."
                })
        
        return cleaned_data

    def save(self, commit=True, user=None):
        """Save the job post with the posting user."""
        instance = super().save(commit=False)
        
        if user:
            instance.posted_by = user
        
        # Set status to pending for review
        instance.status = "pending"
        
        if commit:
            instance.save()
            logger.info(f"Job post created: {instance.title} by {user.email if user else 'unknown'}")
        
        return instance
