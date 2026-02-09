"""
URL routing for the Contact app.
"""

from django.urls import path

from . import views

app_name = "contact"

urlpatterns = [
    path("submit/", views.contact_submit, name="submit"),
]
