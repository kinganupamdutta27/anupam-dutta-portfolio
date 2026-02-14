"""
Authentication views with security features.

All views include:
    - CSRF protection
    - Rate limiting
    - Login history tracking
    - Secure session handling
"""

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.urls import reverse_lazy, reverse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_http_methods

from apps.core.utils import get_client_ip

from .forms import (
    UserRegistrationForm,
    SecureLoginForm,
    PasswordResetRequestForm,
    SecurePasswordChangeForm,
    ProfileUpdateForm,
)
from .models import User, LoginHistory, PasswordResetRequest

logger = logging.getLogger(__name__)


# ==============================================================================
# REGISTRATION VIEW
# ==============================================================================


@method_decorator([csrf_protect, never_cache], name="dispatch")
class RegisterView(View):
    """
    User registration with security features.
    """

    template_name = "accounts/register.html"
    form_class = UserRegistrationForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        
        form = self.form_class(request.POST)
        
        if form.is_valid():
            user = form.save()
            
            # Log the registration
            logger.info(
                f"New user registered: {user.email} from IP {get_client_ip(request)}"
            )
            
            # Auto-login after registration (specify backend for multiple backends)
            login(request, user, backend="apps.accounts.backends.EmailAuthBackend")
            
            messages.success(
                request,
                f"Welcome, {user.get_short_name()}! Your account has been created successfully."
            )
            
            return redirect("accounts:dashboard")
        
        return render(request, self.template_name, {"form": form})


# ==============================================================================
# LOGIN VIEW
# ==============================================================================


@method_decorator([csrf_protect, never_cache], name="dispatch")
class LoginView(View):
    """
    Secure login with account lockout and history tracking.
    """

    template_name = "accounts/login.html"
    form_class = SecureLoginForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        
        form = self.form_class(request, data=request.POST)
        ip_address = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")[:500]
        
        if form.is_valid():
            user = form.get_user()
            
            # Record successful login
            LoginHistory.objects.create(
                user=user,
                email_attempted=user.email,
                ip_address=ip_address,
                user_agent=user_agent,
                success=True,
            )
            user.record_successful_login(ip_address)
            
            # Login the user (specify backend for multiple backends)
            login(request, user, backend="apps.accounts.backends.EmailAuthBackend")
            
            # Handle "remember me"
            if not form.cleaned_data.get("remember_me"):
                request.session.set_expiry(0)  # Browser close
            else:
                request.session.set_expiry(60 * 60 * 24 * 30)  # 30 days
            
            logger.info(f"User logged in: {user.email} from IP {ip_address}")
            
            messages.success(request, f"Welcome back, {user.get_short_name()}!")
            
            # Redirect to next URL or dashboard
            next_url = request.GET.get("next", "")
            if next_url and next_url.startswith("/"):
                return redirect(next_url)
            return redirect("accounts:dashboard")
        
        # Record failed login attempt
        email = request.POST.get("email", "unknown")
        failure_reason = "invalid_credentials"
        
        # Determine specific failure reason
        try:
            user = User.objects.get(email=email.lower())
            if user.is_locked:
                failure_reason = "account_locked"
            elif not user.is_active:
                failure_reason = "account_inactive"
        except User.DoesNotExist:
            pass
        
        LoginHistory.objects.create(
            user=None,
            email_attempted=email,
            ip_address=ip_address,
            user_agent=user_agent,
            success=False,
            failure_reason=failure_reason,
        )
        
        return render(request, self.template_name, {"form": form})


# ==============================================================================
# LOGOUT VIEW
# ==============================================================================


@login_required
@require_http_methods(["GET", "POST"])
@csrf_protect
def logout_view(request):
    """
    Secure logout with session cleanup.
    """
    user_email = request.user.email
    logout(request)
    
    # Clear session data
    request.session.flush()
    
    logger.info(f"User logged out: {user_email}")
    messages.info(request, "You have been logged out successfully.")
    
    return redirect("accounts:login")


# ==============================================================================
# DASHBOARD VIEW
# ==============================================================================


@method_decorator([login_required, never_cache], name="dispatch")
class DashboardView(View):
    """
    User dashboard showing profile and job posts.
    """

    template_name = "accounts/dashboard.html"

    def get(self, request):
        # Get user's job posts
        from apps.jobs.models import JobPost
        
        job_posts = JobPost.objects.filter(
            posted_by=request.user
        ).order_by("-created_at")[:10]
        
        context = {
            "user": request.user,
            "job_posts": job_posts,
            "total_posts": job_posts.count(),
        }
        
        return render(request, self.template_name, context)


# ==============================================================================
# PROFILE VIEW
# ==============================================================================


@method_decorator([login_required, csrf_protect, never_cache], name="dispatch")
class ProfileView(View):
    """
    User profile view and update.
    """

    template_name = "accounts/profile.html"
    form_class = ProfileUpdateForm

    def get(self, request):
        form = self.form_class(instance=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES, instance=request.user)
        
        if form.is_valid():
            form.save()
            messages.success(request, "Your profile has been updated successfully.")
            return redirect("accounts:profile")
        
        return render(request, self.template_name, {"form": form})


# ==============================================================================
# PASSWORD CHANGE VIEW
# ==============================================================================


@method_decorator([login_required, csrf_protect, never_cache], name="dispatch")
class PasswordChangeView(View):
    """
    Secure password change for authenticated users.
    """

    template_name = "accounts/password_change.html"
    form_class = SecurePasswordChangeForm

    def get(self, request):
        form = self.form_class(user=request.user)
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(user=request.user, data=request.POST)
        
        if form.is_valid():
            form.save()
            
            # Keep user logged in after password change
            update_session_auth_hash(request, request.user)
            
            messages.success(
                request,
                "Your password has been changed successfully."
            )
            
            logger.info(f"Password changed for user: {request.user.email}")
            
            return redirect("accounts:dashboard")
        
        return render(request, self.template_name, {"form": form})


# ==============================================================================
# PASSWORD RESET REQUEST VIEW
# ==============================================================================


@method_decorator([csrf_protect, never_cache], name="dispatch")
class PasswordResetRequestView(View):
    """
    Request password reset (admin-controlled).
    
    Users cannot reset their own passwords - they must request
    a reset which an admin will process manually.
    """

    template_name = "accounts/password_reset_request.html"
    form_class = PasswordResetRequestForm

    def get(self, request):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        if request.user.is_authenticated:
            return redirect("accounts:dashboard")
        
        form = self.form_class(request.POST)
        
        if form.is_valid():
            ip_address = get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")
            
            # Save the request (may be None if user doesn't exist)
            form.save(
                commit=True,
                ip_address=ip_address,
                user_agent=user_agent,
            )
            
            # Always show success message (don't reveal if user exists)
            messages.success(
                request,
                "Your password reset request has been submitted. "
                "An administrator will review it and contact you via email."
            )
            
            return redirect("accounts:login")
        
        return render(request, self.template_name, {"form": form})


# ==============================================================================
# PASSWORD RESET REQUEST STATUS VIEW
# ==============================================================================


@method_decorator([login_required, never_cache], name="dispatch")
class PasswordResetStatusView(View):
    """
    View status of password reset requests.
    """

    template_name = "accounts/password_reset_status.html"

    def get(self, request):
        requests = PasswordResetRequest.objects.filter(
            user=request.user
        ).order_by("-created_at")[:5]
        
        return render(request, self.template_name, {"requests": requests})
