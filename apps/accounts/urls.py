"""
URL configuration for the accounts app.
"""

from django.urls import path

from . import views

app_name = "accounts"

urlpatterns = [
    # Authentication
    path("register/", views.RegisterView.as_view(), name="register"),
    path("login/", views.LoginView.as_view(), name="login"),
    path("logout/", views.logout_view, name="logout"),
    
    # Dashboard & Profile
    path("dashboard/", views.DashboardView.as_view(), name="dashboard"),
    path("profile/", views.ProfileView.as_view(), name="profile"),
    
    # Password Management
    path("password/change/", views.PasswordChangeView.as_view(), name="password_change"),
    path("password/reset/request/", views.PasswordResetRequestView.as_view(), name="password_reset_request"),
    path("password/reset/status/", views.PasswordResetStatusView.as_view(), name="password_reset_status"),
]
