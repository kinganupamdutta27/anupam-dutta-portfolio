"""
Test factories for the Portfolio app models.
"""

import datetime

import factory

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


class SkillCategoryFactory(factory.django.DjangoModelFactory):
    """Factory for creating SkillCategory instances."""

    class Meta:
        model = SkillCategory

    name = factory.Sequence(lambda n: f"Skill Category {n}")
    icon_class = "fas fa-code"
    sort_order = factory.Sequence(lambda n: n)
    is_active = True


class SkillFactory(factory.django.DjangoModelFactory):
    """Factory for creating Skill instances."""

    class Meta:
        model = Skill

    category = factory.SubFactory(SkillCategoryFactory)
    name = factory.Sequence(lambda n: f"Skill {n}")
    sort_order = factory.Sequence(lambda n: n)


class ExperienceFactory(factory.django.DjangoModelFactory):
    """Factory for creating Experience instances."""

    class Meta:
        model = Experience

    job_title = factory.Sequence(lambda n: f"Job Title {n}")
    company_name = factory.Sequence(lambda n: f"Company {n}")
    location = "Test City"
    start_date = factory.LazyFunction(lambda: datetime.date(2024, 1, 1))
    end_date = None
    is_current = True
    sort_order = factory.Sequence(lambda n: n)
    is_active = True


class ExperienceHighlightFactory(factory.django.DjangoModelFactory):
    """Factory for creating ExperienceHighlight instances."""

    class Meta:
        model = ExperienceHighlight

    experience = factory.SubFactory(ExperienceFactory)
    text = factory.Sequence(lambda n: f"Achievement highlight number {n}")
    sort_order = factory.Sequence(lambda n: n)


class ProjectFactory(factory.django.DjangoModelFactory):
    """Factory for creating Project instances."""

    class Meta:
        model = Project

    title = factory.Sequence(lambda n: f"Project {n}")
    description = "A test project description."
    live_url = "https://example.com"
    github_url = "https://github.com/test/project"
    is_featured = True
    sort_order = factory.Sequence(lambda n: n)
    is_active = True


class ProjectTechnologyFactory(factory.django.DjangoModelFactory):
    """Factory for creating ProjectTechnology instances."""

    class Meta:
        model = ProjectTechnology

    project = factory.SubFactory(ProjectFactory)
    name = factory.Sequence(lambda n: f"Tech {n}")
    sort_order = factory.Sequence(lambda n: n)


class EducationFactory(factory.django.DjangoModelFactory):
    """Factory for creating Education instances."""

    class Meta:
        model = Education

    degree = factory.Sequence(lambda n: f"B.Tech in Field {n}")
    institution = factory.Sequence(lambda n: f"University {n}")
    start_year = 2020
    end_year = 2024
    grade = "GPA: 8.5"
    sort_order = factory.Sequence(lambda n: n)
    is_active = True


class CertificationFactory(factory.django.DjangoModelFactory):
    """Factory for creating Certification instances."""

    class Meta:
        model = Certification

    name = factory.Sequence(lambda n: f"Certification {n}")
    issuer = factory.Sequence(lambda n: f"Issuer {n}")
    icon_class = "fab fa-aws"
    sort_order = factory.Sequence(lambda n: n)
    is_active = True
