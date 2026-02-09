"""
Django admin configuration for ContactSubmission.

Uses Unfold ModelAdmin for a modern admin experience.
"""

from django.contrib import admin
from unfold.admin import ModelAdmin
from unfold.decorators import display

from .models import ContactSubmission


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(ModelAdmin):
    """
    Admin configuration for ContactSubmission model.

    Provides a clean interface for managing contact form submissions
    with filtering, search, and bulk actions.
    """

    list_display = [
        "name",
        "email",
        "short_message",
        "display_read_status",
        "created_at",
    ]
    list_filter = ["is_read", "created_at"]
    search_fields = ["name", "email", "message"]
    readonly_fields = [
        "name",
        "email",
        "message",
        "created_at",
        "ip_address",
        "user_agent",
    ]
    list_per_page = 25
    ordering = ["-created_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        (
            "Message Details",
            {
                "fields": ("name", "email", "message"),
            },
        ),
        (
            "Status",
            {
                "fields": ("is_read",),
            },
        ),
        (
            "Metadata",
            {
                "fields": ("created_at", "ip_address", "user_agent"),
                "classes": ("collapse",),
            },
        ),
    )

    actions = ["mark_as_read", "mark_as_unread"]

    @display(description="Message", ordering="message")
    def short_message(self, obj):
        """Display truncated message preview."""
        if len(obj.message) > 80:
            return f"{obj.message[:80]}..."
        return obj.message

    @display(
        description="Status",
        ordering="is_read",
        label={
            True: "success",
            False: "warning",
        },
    )
    def display_read_status(self, obj):
        return obj.is_read

    @admin.action(description="Mark selected as read")
    def mark_as_read(self, request, queryset):
        updated = queryset.update(is_read=True)
        self.message_user(request, f"{updated} submission(s) marked as read.")

    @admin.action(description="Mark selected as unread")
    def mark_as_unread(self, request, queryset):
        updated = queryset.update(is_read=False)
        self.message_user(request, f"{updated} submission(s) marked as unread.")

    def has_add_permission(self, request):
        """Disable adding submissions through admin."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Allow deletion of submissions."""
        return True
