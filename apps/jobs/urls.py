"""
URL configuration for the jobs app.
"""

from django.urls import path

from . import views

app_name = "jobs"

urlpatterns = [
    # Job management
    path("", views.MyJobsView.as_view(), name="my_jobs"),
    path("create/", views.CreateJobView.as_view(), name="create_job"),
    path("<slug:slug>/", views.JobDetailView.as_view(), name="job_detail"),
    path("<slug:slug>/edit/", views.EditJobView.as_view(), name="edit_job"),
    path("<slug:slug>/delete/", views.DeleteJobView.as_view(), name="delete_job"),
    path("<slug:slug>/close/", views.CloseJobView.as_view(), name="close_job"),
]
