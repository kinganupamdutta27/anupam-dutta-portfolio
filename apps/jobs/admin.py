"""
Admin configuration for the jobs app.

Uses Unfold for modern admin interface.
Admins can review, approve, or reject job postings.
"""

from django.contrib import admin
from django.contrib import messages
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import JobPost


@admin.register(JobPost)
class JobPostAdmin(ModelAdmin):
    """
    Admin for managing job postings.
    
    Admins can review, approve, or reject job posts submitted by users.
    """

    list_display = [
        "title",
        "company_name",
        "posted_by",
        "status_badge",
        "job_type",
        "location",
        "created_at",
    ]
    list_filter = [
        "status",
        "job_type",
        "experience_level",
        "is_remote",
        "created_at",
    ]
    search_fields = [
        "title",
        "company_name",
        "posted_by__email",
        "posted_by__full_name",
        "location",
        "skills_required",
    ]
    readonly_fields = [
        "slug",
        "posted_by",
        "created_at",
        "updated_at",
        "reviewed_by",
        "reviewed_at",
    ]
    ordering = ["-created_at"]
    prepopulated_fields = {}  # Slug is auto-generated

    fieldsets = (
        ("Job Information", {
            "fields": (
                "title",
                "slug",
                "company_name",
                "company_website",
                "company_logo",
            ),
        }),
        ("Job Details", {
            "fields": (
                "description",
                "requirements",
                "responsibilities",
                "benefits",
            ),
        }),
        ("Classification", {
            "fields": (
                "job_type",
                "experience_level",
                "location",
                "is_remote",
                "skills_required",
            ),
        }),
        ("Compensation", {
            "fields": (
                "salary_min",
                "salary_max",
                "salary_currency",
                "show_salary",
            ),
        }),
        ("Contact", {
            "fields": (
                "contact_email",
                "contact_phone",
                "application_url",
            ),
        }),
        ("Status & Review", {
            "fields": (
                "status",
                "rejection_reason",
                "reviewed_by",
                "reviewed_at",
                "expires_at",
            ),
        }),
        ("Ownership", {
            "fields": (
                "posted_by",
                "created_at",
                "updated_at",
            ),
        }),
    )

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            "draft": "#6b7280",      # Gray
            "pending": "#f59e0b",    # Yellow
            "approved": "#10b981",   # Green
            "rejected": "#ef4444",   # Red
            "closed": "#3b82f6",     # Blue
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display(),
        )

    actions = ["approve_jobs", "reject_jobs", "close_jobs"]

    @action(description="Approve selected job posts")
    def approve_jobs(self, request, queryset):
        """Approve selected job postings."""
        count = 0
        for job in queryset.filter(status="pending"):
            job.approve(request.user)
            count += 1
        
        self.message_user(
            request,
            f"{count} job post(s) have been approved.",
            messages.SUCCESS,
        )

    @action(description="Reject selected job posts")
    def reject_jobs(self, request, queryset):
        """Reject selected job postings."""
        count = 0
        for job in queryset.filter(status="pending"):
            job.reject(request.user, reason="Rejected by administrator.")
            count += 1
        
        self.message_user(
            request,
            f"{count} job post(s) have been rejected.",
            messages.WARNING,
        )

    @action(description="Close selected job posts")
    def close_jobs(self, request, queryset):
        """Close selected job postings."""
        count = queryset.exclude(status="closed").update(status="closed")
        
        self.message_user(
            request,
            f"{count} job post(s) have been closed.",
            messages.INFO,
        )

    def has_add_permission(self, request):
        """Admins can add jobs directly if needed."""
        return request.user.is_superuser

    def save_model(self, request, obj, form, change):
        """Set reviewed_by when status changes."""
        if change:
            original = JobPost.objects.get(pk=obj.pk)
            if original.status != obj.status and obj.status in ["approved", "rejected"]:
                obj.reviewed_by = request.user
                from django.utils import timezone
                obj.reviewed_at = timezone.now()
        super().save_model(request, obj, form, change)
