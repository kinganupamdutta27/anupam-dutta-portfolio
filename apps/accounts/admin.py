"""
Admin configuration for the accounts app.

Uses Unfold for modern admin interface.
"""

import secrets
import string

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib import messages
from django.utils import timezone
from django.utils.html import format_html

from unfold.admin import ModelAdmin
from unfold.decorators import action

from .models import User, PasswordResetRequest, LoginHistory


# ==============================================================================
# USER ADMIN
# ==============================================================================


@admin.register(User)
class UserAdmin(BaseUserAdmin, ModelAdmin):
    """
    Custom User admin with Unfold styling.
    """

    list_display = [
        "email",
        "full_name",
        "company",
        "is_active",
        "is_verified",
        "is_locked_display",
        "created_at",
    ]
    list_filter = [
        "is_active",
        "is_verified",
        "is_staff",
        "is_superuser",
        "created_at",
    ]
    search_fields = ["email", "full_name", "company"]
    ordering = ["-created_at"]
    readonly_fields = [
        "created_at",
        "updated_at",
        "last_login",
        "last_login_ip",
        "last_password_change",
        "failed_login_attempts",
        "lockout_until",
    ]

    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal Info", {"fields": ("full_name", "phone", "company", "bio", "profile_image")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "is_verified", "groups", "user_permissions")}),
        ("Security", {"fields": ("failed_login_attempts", "lockout_until", "last_login_ip", "last_password_change")}),
        ("Important Dates", {"fields": ("last_login", "created_at", "updated_at")}),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "full_name", "password1", "password2", "is_active", "is_staff"),
        }),
    )

    @admin.display(description="Locked", boolean=True)
    def is_locked_display(self, obj):
        return obj.is_locked

    actions = ["unlock_accounts", "verify_accounts", "deactivate_accounts"]

    @action(description="Unlock selected accounts")
    def unlock_accounts(self, request, queryset):
        count = queryset.update(
            failed_login_attempts=0,
            lockout_until=None,
        )
        self.message_user(
            request,
            f"{count} account(s) have been unlocked.",
            messages.SUCCESS,
        )

    @action(description="Mark as verified")
    def verify_accounts(self, request, queryset):
        count = queryset.update(is_verified=True)
        self.message_user(
            request,
            f"{count} account(s) have been verified.",
            messages.SUCCESS,
        )

    @action(description="Deactivate selected accounts")
    def deactivate_accounts(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f"{count} account(s) have been deactivated.",
            messages.WARNING,
        )


# ==============================================================================
# PASSWORD RESET REQUEST ADMIN
# ==============================================================================


@admin.register(PasswordResetRequest)
class PasswordResetRequestAdmin(ModelAdmin):
    """
    Admin for managing password reset requests.
    
    Admins can approve requests and generate temporary passwords.
    """

    list_display = [
        "user",
        "status_badge",
        "request_ip",
        "created_at",
        "processed_by",
        "processed_at",
    ]
    list_filter = ["status", "created_at"]
    search_fields = ["user__email", "user__full_name", "reason"]
    readonly_fields = [
        "user",
        "reason",
        "request_ip",
        "user_agent",
        "created_at",
        "updated_at",
        "processed_by",
        "processed_at",
    ]
    ordering = ["-created_at"]

    fieldsets = (
        ("Request Details", {
            "fields": ("user", "reason", "status"),
        }),
        ("Security Info", {
            "fields": ("request_ip", "user_agent"),
        }),
        ("Admin Processing", {
            "fields": ("processed_by", "processed_at", "admin_notes"),
        }),
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
        }),
    )

    @admin.display(description="Status")
    def status_badge(self, obj):
        colors = {
            "pending": "#f59e0b",  # Yellow
            "approved": "#10b981",  # Green
            "rejected": "#ef4444",  # Red
        }
        color = colors.get(obj.status, "#6b7280")
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px; font-weight: 600;">{}</span>',
            color,
            obj.get_status_display(),
        )

    actions = ["approve_and_generate_password", "reject_requests"]

    @action(description="Approve & Generate Temporary Password")
    def approve_and_generate_password(self, request, queryset):
        """
        Approve selected requests and generate temporary passwords.
        """
        approved_count = 0
        
        for reset_request in queryset.filter(status="pending"):
            # Generate a secure temporary password
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            temp_password = "".join(secrets.choice(alphabet) for _ in range(16))
            
            # Approve the request
            reset_request.approve(
                admin_user=request.user,
                temp_password=temp_password,
            )
            
            approved_count += 1
            
            # Show the temporary password to admin
            self.message_user(
                request,
                f"Password for {reset_request.user.email}: {temp_password}",
                messages.INFO,
            )
        
        if approved_count > 0:
            self.message_user(
                request,
                f"{approved_count} request(s) approved. "
                "Please securely communicate the temporary passwords to users.",
                messages.SUCCESS,
            )

    @action(description="Reject selected requests")
    def reject_requests(self, request, queryset):
        """Reject selected password reset requests."""
        count = 0
        for reset_request in queryset.filter(status="pending"):
            reset_request.reject(
                admin_user=request.user,
                reason="Request rejected by administrator.",
            )
            count += 1
        
        self.message_user(
            request,
            f"{count} request(s) have been rejected.",
            messages.WARNING,
        )


# ==============================================================================
# LOGIN HISTORY ADMIN
# ==============================================================================


@admin.register(LoginHistory)
class LoginHistoryAdmin(ModelAdmin):
    """
    Admin for viewing login history (read-only).
    """

    list_display = [
        "email_attempted",
        "success_badge",
        "failure_reason",
        "ip_address",
        "timestamp",
    ]
    list_filter = ["success", "failure_reason", "timestamp"]
    search_fields = ["email_attempted", "ip_address"]
    readonly_fields = [
        "user",
        "email_attempted",
        "ip_address",
        "user_agent",
        "success",
        "failure_reason",
        "timestamp",
    ]
    ordering = ["-timestamp"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        # Only superusers can delete login history
        return request.user.is_superuser

    @admin.display(description="Status")
    def success_badge(self, obj):
        if obj.success:
            return format_html(
                '<span style="background-color: #10b981; color: white; padding: 3px 8px; '
                'border-radius: 4px; font-size: 11px;">Success</span>'
            )
        return format_html(
            '<span style="background-color: #ef4444; color: white; padding: 3px 8px; '
            'border-radius: 4px; font-size: 11px;">Failed</span>'
        )
