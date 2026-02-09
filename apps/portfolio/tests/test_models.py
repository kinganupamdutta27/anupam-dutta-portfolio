"""
Tests for Portfolio app models.

Tests cover:
    - Model creation and string representations
    - Field validations (date ranges, year ranges)
    - Model properties (date_range, company_display, is_expired, etc.)
    - Queryset filtering (active items, featured projects)
    - Ordering behavior
"""

import datetime

import pytest
from django.core.exceptions import ValidationError

from apps.portfolio.models import (
    Certification,
    Education,
    Experience,
    ExperienceHighlight,
    Project,
    ProjectTechnology,
    Skill,
    SkillCategory,
)
from .factories import (
    CertificationFactory,
    EducationFactory,
    ExperienceFactory,
    ExperienceHighlightFactory,
    ProjectFactory,
    ProjectTechnologyFactory,
    SkillCategoryFactory,
    SkillFactory,
)


@pytest.mark.django_db
class TestSkillCategory:
    """Tests for SkillCategory and Skill models."""

    def test_create_skill_category(self):
        """Test creating a skill category."""
        category = SkillCategoryFactory(name="Programming Languages")
        assert category.pk is not None
        assert str(category) == "Programming Languages"

    def test_skill_count_property(self):
        """Test the skill_count property."""
        category = SkillCategoryFactory()
        SkillFactory(category=category, name="Python")
        SkillFactory(category=category, name="JavaScript")
        assert category.skill_count == 2

    def test_skill_str(self):
        """Test Skill string representation."""
        skill = SkillFactory(name="FastAPI")
        assert str(skill) == "FastAPI"

    def test_skill_category_ordering(self):
        """Test that categories are ordered by sort_order."""
        SkillCategoryFactory(name="B", sort_order=2)
        SkillCategoryFactory(name="A", sort_order=1)
        categories = list(SkillCategory.objects.all())
        assert categories[0].name == "A"
        assert categories[1].name == "B"

    def test_inactive_category_filtered(self):
        """Test filtering inactive categories."""
        SkillCategoryFactory(is_active=True)
        SkillCategoryFactory(is_active=False)
        active = SkillCategory.objects.filter(is_active=True)
        assert active.count() == 1


@pytest.mark.django_db
class TestExperience:
    """Tests for Experience and ExperienceHighlight models."""

    def test_create_experience(self):
        """Test creating an experience entry."""
        exp = ExperienceFactory(
            job_title="Python Developer",
            company_name="Test Corp",
        )
        assert exp.pk is not None
        assert str(exp) == "Python Developer at Test Corp"

    def test_date_range_current(self):
        """Test date_range for a current position."""
        exp = ExperienceFactory(
            start_date=datetime.date(2024, 4, 1),
            is_current=True,
            end_date=None,
        )
        assert "April 2024" in exp.date_range
        assert "Present" in exp.date_range

    def test_date_range_past(self):
        """Test date_range for a past position."""
        exp = ExperienceFactory(
            start_date=datetime.date(2023, 11, 1),
            end_date=datetime.date(2024, 3, 31),
            is_current=False,
        )
        assert "November 2023" in exp.date_range
        assert "March 2024" in exp.date_range

    def test_company_display_with_location(self):
        """Test company_display with location."""
        exp = ExperienceFactory(company_name="Weavers Web", location="Kolkata")
        assert exp.company_display == "Weavers Web \u2022 Kolkata"

    def test_company_display_without_location(self):
        """Test company_display without location."""
        exp = ExperienceFactory(company_name="Weavers Web", location="")
        assert exp.company_display == "Weavers Web"

    def test_end_date_before_start_date_raises_error(self):
        """Test that end_date before start_date raises ValidationError."""
        exp = Experience(
            job_title="Test",
            company_name="Test",
            start_date=datetime.date(2024, 6, 1),
            end_date=datetime.date(2024, 1, 1),
            is_current=False,
        )
        with pytest.raises(ValidationError) as exc_info:
            exp.clean()
        assert "end_date" in exc_info.value.message_dict

    def test_current_with_end_date_raises_error(self):
        """Test that current position with end_date raises ValidationError."""
        exp = Experience(
            job_title="Test",
            company_name="Test",
            start_date=datetime.date(2024, 1, 1),
            end_date=datetime.date(2024, 6, 1),
            is_current=True,
        )
        with pytest.raises(ValidationError) as exc_info:
            exp.clean()
        assert "end_date" in exc_info.value.message_dict

    def test_experience_highlight_str(self):
        """Test ExperienceHighlight string representation."""
        highlight = ExperienceHighlightFactory(text="Built scalable APIs")
        assert str(highlight) == "Built scalable APIs"

    def test_experience_highlight_long_text_truncated(self):
        """Test that long highlight text is truncated in str."""
        long_text = "A" * 100
        highlight = ExperienceHighlightFactory(text=long_text)
        assert len(str(highlight)) <= 83  # 80 chars + "..."

    def test_experience_ordering(self):
        """Test that experiences are ordered by start_date descending."""
        ExperienceFactory(
            job_title="Old Job",
            start_date=datetime.date(2023, 1, 1),
            is_current=False,
        )
        ExperienceFactory(
            job_title="New Job",
            start_date=datetime.date(2024, 1, 1),
            is_current=True,
        )
        experiences = list(Experience.objects.all())
        assert experiences[0].job_title == "New Job"


@pytest.mark.django_db
class TestProject:
    """Tests for Project and ProjectTechnology models."""

    def test_create_project(self):
        """Test creating a project."""
        project = ProjectFactory(title="Plugg")
        assert project.pk is not None
        assert str(project) == "Plugg"

    def test_has_links_both(self):
        """Test has_links with both URLs."""
        project = ProjectFactory(
            live_url="https://example.com",
            github_url="https://github.com/test",
        )
        assert project.has_links is True

    def test_has_links_none(self):
        """Test has_links with no URLs."""
        project = ProjectFactory(live_url="", github_url="")
        assert project.has_links is False

    def test_technology_list(self):
        """Test technology_list property."""
        project = ProjectFactory()
        ProjectTechnologyFactory(project=project, name="Python")
        ProjectTechnologyFactory(project=project, name="Django")
        assert "Python" in project.technology_list
        assert "Django" in project.technology_list

    def test_featured_projects_filter(self):
        """Test filtering featured projects."""
        ProjectFactory(is_featured=True)
        ProjectFactory(is_featured=False)
        featured = Project.objects.filter(is_featured=True, is_active=True)
        assert featured.count() == 1


@pytest.mark.django_db
class TestEducation:
    """Tests for the Education model."""

    def test_create_education(self):
        """Test creating an education entry."""
        edu = EducationFactory(
            degree="B.Tech in CSE",
            institution="Test University",
        )
        assert str(edu) == "B.Tech in CSE - Test University"

    def test_year_range(self):
        """Test year_range property."""
        edu = EducationFactory(start_year=2020, end_year=2023)
        assert edu.year_range == "2020 - 2023"

    def test_end_year_before_start_year_raises_error(self):
        """Test that end_year before start_year raises ValidationError."""
        edu = Education(
            degree="Test",
            institution="Test",
            start_year=2024,
            end_year=2020,
        )
        with pytest.raises(ValidationError) as exc_info:
            edu.clean()
        assert "end_year" in exc_info.value.message_dict


@pytest.mark.django_db
class TestCertification:
    """Tests for the Certification model."""

    def test_create_certification(self):
        """Test creating a certification."""
        cert = CertificationFactory(
            name="AWS Cloud Foundations",
            issuer="Amazon Web Services",
        )
        assert str(cert) == "AWS Cloud Foundations - Amazon Web Services"

    def test_is_expired_no_expiry(self):
        """Test is_expired with no expiry date."""
        cert = CertificationFactory(expiry_date=None)
        assert cert.is_expired is False

    def test_is_expired_future_date(self):
        """Test is_expired with future expiry date."""
        cert = CertificationFactory(
            expiry_date=datetime.date(2030, 12, 31),
        )
        assert cert.is_expired is False

    def test_is_expired_past_date(self):
        """Test is_expired with past expiry date."""
        cert = CertificationFactory(
            expiry_date=datetime.date(2020, 1, 1),
        )
        assert cert.is_expired is True
