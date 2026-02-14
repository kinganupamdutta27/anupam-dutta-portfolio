"""
Job posting views.
"""

import logging

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render, redirect, get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect

from .forms import JobPostForm
from .models import JobPost

logger = logging.getLogger(__name__)


# ==============================================================================
# JOB LIST VIEW (User's own jobs)
# ==============================================================================


@method_decorator([login_required, never_cache], name="dispatch")
class MyJobsView(View):
    """
    List all job posts by the current user.
    """

    template_name = "jobs/my_jobs.html"

    def get(self, request):
        jobs = JobPost.objects.filter(
            posted_by=request.user
        ).order_by("-created_at")
        
        # Group by status
        pending_jobs = jobs.filter(status="pending")
        approved_jobs = jobs.filter(status="approved")
        rejected_jobs = jobs.filter(status="rejected")
        closed_jobs = jobs.filter(status="closed")
        
        context = {
            "jobs": jobs,
            "pending_jobs": pending_jobs,
            "approved_jobs": approved_jobs,
            "rejected_jobs": rejected_jobs,
            "closed_jobs": closed_jobs,
            "total_count": jobs.count(),
        }
        
        return render(request, self.template_name, context)


# ==============================================================================
# CREATE JOB VIEW
# ==============================================================================


@method_decorator([login_required, csrf_protect, never_cache], name="dispatch")
class CreateJobView(View):
    """
    Create a new job posting.
    """

    template_name = "jobs/create_job.html"
    form_class = JobPostForm

    def get(self, request):
        form = self.form_class()
        return render(request, self.template_name, {"form": form})

    def post(self, request):
        form = self.form_class(request.POST, request.FILES)
        
        if form.is_valid():
            job = form.save(commit=True, user=request.user)
            
            messages.success(
                request,
                f"Your job posting '{job.title}' has been submitted for review. "
                "You will be notified once it's approved."
            )
            
            logger.info(
                f"Job post created: {job.title} by {request.user.email}"
            )
            
            return redirect("jobs:my_jobs")
        
        return render(request, self.template_name, {"form": form})


# ==============================================================================
# EDIT JOB VIEW
# ==============================================================================


@method_decorator([login_required, csrf_protect, never_cache], name="dispatch")
class EditJobView(View):
    """
    Edit an existing job posting.
    
    Only the owner can edit, and only if status is draft or pending.
    """

    template_name = "jobs/edit_job.html"
    form_class = JobPostForm

    def get_object(self, request, slug):
        """Get job post and verify ownership."""
        job = get_object_or_404(JobPost, slug=slug)
        
        if job.posted_by != request.user:
            raise Http404("Job not found")
        
        return job

    def get(self, request, slug):
        job = self.get_object(request, slug)
        
        # Only allow editing if pending or draft
        if job.status not in ["draft", "pending"]:
            messages.error(
                request,
                "You cannot edit a job posting that has already been reviewed."
            )
            return redirect("jobs:my_jobs")
        
        form = self.form_class(instance=job)
        return render(request, self.template_name, {"form": form, "job": job})

    def post(self, request, slug):
        job = self.get_object(request, slug)
        
        if job.status not in ["draft", "pending"]:
            messages.error(
                request,
                "You cannot edit a job posting that has already been reviewed."
            )
            return redirect("jobs:my_jobs")
        
        form = self.form_class(request.POST, request.FILES, instance=job)
        
        if form.is_valid():
            form.save()
            
            messages.success(
                request,
                f"Your job posting '{job.title}' has been updated."
            )
            
            return redirect("jobs:my_jobs")
        
        return render(request, self.template_name, {"form": form, "job": job})


# ==============================================================================
# VIEW JOB DETAIL
# ==============================================================================


@method_decorator([login_required, never_cache], name="dispatch")
class JobDetailView(View):
    """
    View job posting details.
    """

    template_name = "jobs/job_detail.html"

    def get(self, request, slug):
        job = get_object_or_404(JobPost, slug=slug)
        
        # Only owner can view their own pending/rejected jobs
        if job.posted_by != request.user and job.status != "approved":
            raise Http404("Job not found")
        
        return render(request, self.template_name, {"job": job})


# ==============================================================================
# DELETE JOB VIEW
# ==============================================================================


@method_decorator([login_required, csrf_protect, never_cache], name="dispatch")
class DeleteJobView(View):
    """
    Delete a job posting.
    
    Only the owner can delete.
    """

    def post(self, request, slug):
        job = get_object_or_404(JobPost, slug=slug, posted_by=request.user)
        
        title = job.title
        job.delete()
        
        messages.success(
            request,
            f"Job posting '{title}' has been deleted."
        )
        
        logger.info(
            f"Job post deleted: {title} by {request.user.email}"
        )
        
        return redirect("jobs:my_jobs")


# ==============================================================================
# CLOSE JOB VIEW
# ==============================================================================


@method_decorator([login_required, csrf_protect, never_cache], name="dispatch")
class CloseJobView(View):
    """
    Close a job posting (mark as filled/closed).
    """

    def post(self, request, slug):
        job = get_object_or_404(JobPost, slug=slug, posted_by=request.user)
        
        job.close()
        
        messages.success(
            request,
            f"Job posting '{job.title}' has been closed."
        )
        
        return redirect("jobs:my_jobs")
