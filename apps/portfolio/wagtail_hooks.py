"""
Wagtail hooks for the Portfolio app.

Provides customization of snippet admin views for portfolio content.
"""

from wagtail import hooks
from wagtail.snippets.models import register_snippet
from wagtail.snippets.views.snippets import SnippetViewSet

from .models import Certification, Education, Experience, Project, SkillCategory


class SkillCategoryViewSet(SnippetViewSet):
    model = SkillCategory
    icon = "code"
    menu_label = "Skills"
    menu_name = "skills"
    menu_order = 200
    add_to_admin_menu = True
    list_display = ["name", "icon_class", "sort_order", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name"]


class ExperienceViewSet(SnippetViewSet):
    model = Experience
    icon = "date"
    menu_label = "Experience"
    menu_name = "experience"
    menu_order = 210
    add_to_admin_menu = True
    list_display = ["job_title", "company_name", "location", "start_date", "is_current", "is_active"]
    list_filter = ["is_active", "is_current"]
    search_fields = ["job_title", "company_name"]


class ProjectViewSet(SnippetViewSet):
    model = Project
    icon = "folder-open-inverse"
    menu_label = "Projects"
    menu_name = "projects"
    menu_order = 220
    add_to_admin_menu = True
    list_display = ["title", "is_featured", "sort_order", "is_active"]
    list_filter = ["is_active", "is_featured"]
    search_fields = ["title", "description"]


class EducationViewSet(SnippetViewSet):
    model = Education
    icon = "openquote"
    menu_label = "Education"
    menu_name = "education"
    menu_order = 230
    add_to_admin_menu = True
    list_display = ["degree", "institution", "start_year", "end_year", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["degree", "institution"]


class CertificationViewSet(SnippetViewSet):
    model = Certification
    icon = "tick"
    menu_label = "Certifications"
    menu_name = "certifications"
    menu_order = 240
    add_to_admin_menu = True
    list_display = ["name", "issuer", "sort_order", "is_active"]
    list_filter = ["is_active"]
    search_fields = ["name", "issuer"]


# Register custom viewsets (this replaces the @register_snippet on models)
# We need to unregister the default ones first and register with viewsets
register_snippet(SkillCategoryViewSet)
register_snippet(ExperienceViewSet)
register_snippet(ProjectViewSet)
register_snippet(EducationViewSet)
register_snippet(CertificationViewSet)
