"""
Management command to seed the database with portfolio data.

Populates all content from Anupam Dutta's portfolio:
    - HomePage with hero, about, and contact sections
    - Skill categories and individual skills
    - Work experience with highlights
    - Projects with technologies
    - Education entries
    - Certifications
    - Site configuration

Usage:
    python manage.py seed_data
    python manage.py seed_data --flush  # Clear and re-seed
"""

import datetime
import logging

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from wagtail.models import Page, Site

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = "Seed the database with Anupam Dutta's portfolio data."

    def add_arguments(self, parser):
        parser.add_argument(
            "--flush",
            action="store_true",
            help="Clear existing portfolio data before seeding.",
        )

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                if options["flush"]:
                    self._flush_data()

                self._seed_home_page()
                self._seed_skills()
                self._seed_experience()
                self._seed_projects()
                self._seed_education()
                self._seed_certifications()
                self._seed_site_config()

            self.stdout.write(self.style.SUCCESS(
                "\n=== Portfolio data seeded successfully! ===\n"
                "Access the CMS at: http://localhost:8000/cms/\n"
                "Access Django Admin at: http://localhost:8000/admin/\n"
            ))

        except Exception as e:
            logger.error(f"Seed data error: {e}", exc_info=True)
            raise CommandError(f"Failed to seed data: {e}")

    def _flush_data(self):
        """Remove existing portfolio data."""
        from apps.home.models import HomePage, SiteConfiguration
        from apps.portfolio.models import (
            Certification, Education, Experience, Project, SkillCategory,
        )

        self.stdout.write("Flushing existing data...")
        Certification.objects.all().delete()
        Education.objects.all().delete()
        Project.objects.all().delete()
        Experience.objects.all().delete()
        SkillCategory.objects.all().delete()
        HomePage.objects.all().delete()
        self.stdout.write(self.style.WARNING("  Existing data cleared."))

    def _seed_home_page(self):
        """Create the HomePage with all sections."""
        from apps.home.models import (
            AboutStat, ContactLink, HeroSocialLink, HeroTypingText, HomePage,
        )

        if HomePage.objects.exists():
            self.stdout.write(self.style.WARNING("  HomePage already exists. Skipping."))
            return

        self.stdout.write("Creating HomePage...")

        root_page = Page.objects.first()
        if not root_page:
            raise CommandError("No root page found. Run 'python manage.py migrate' first.")

        # Remove default Wagtail "Welcome" page if it exists
        default_pages = Page.objects.filter(slug="home", depth=2).exclude(
            content_type__model="homepage"
        )
        if default_pages.exists():
            for dp in default_pages:
                dp.delete()
            self.stdout.write(self.style.WARNING("  Removed default Wagtail welcome page."))
            # Refresh root page from database after deletion
            root_page = Page.objects.get(pk=root_page.pk)
            # Fix treebeard tree structure
            Page.fix_tree()

        home_page = HomePage(
            title="Anupam Dutta | Python Backend Engineer & GenAI Specialist",
            slug="home",
            seo_title="Anupam Dutta | Python Backend Engineer & GenAI Specialist",
            hero_tag_text="Available for opportunities",
            hero_greeting="Hi, I'm",
            hero_name="Anupam Dutta",
            hero_cta_primary_text="Get in Touch",
            hero_cta_primary_url="#contact",
            hero_cta_primary_icon="fas fa-paper-plane",
            hero_cta_secondary_text="View Projects",
            hero_cta_secondary_url="#projects",
            hero_cta_secondary_icon="fas fa-code",
            about_section_label="About Me",
            about_section_title="Passionate about",
            about_section_title_highlight="Innovative Solutions",
            about_description=(
                "<p>I am a <strong>Computer Science Engineer</strong> and "
                "<strong>Python Backend Developer</strong> with experience building "
                "scalable web applications, Generative AI solutions, and "
                "enterprise-grade systems.</p>"
                "<p>Currently working as a <strong>Junior Python Developer at Weavers Web</strong>, "
                "I focus on backend engineering using Python, FastAPI, Django, RESTful APIs, "
                "and microservices architectures, with a strong emphasis on performance, "
                "scalability, and maintainability.</p>"
                "<p>My recent work involves designing and implementing "
                "<strong>Generative AI and LLM-based systems</strong>, including RAG pipelines "
                "and agentic workflows using <strong>LangChain</strong> and "
                "<strong>LangGraph</strong>.</p>"
            ),
            contact_section_label="Get in Touch",
            contact_section_title="Let's",
            contact_section_title_highlight="Connect",
            contact_heading="Let's work together!",
            contact_description=(
                "I'm always interested in hearing about new projects and opportunities. "
                "Whether you have a question or just want to say hi, feel free to reach out!"
            ),
            contact_email="anupamdutta27121998.in@gmail.com",
        )
        root_page.add_child(instance=home_page)

        # Ensure the Site points to our homepage
        site, _ = Site.objects.get_or_create(
            is_default_site=True,
            defaults={
                "hostname": "localhost",
                "port": 80,
                "root_page": home_page,
                "site_name": "Anupam Dutta Portfolio",
            },
        )
        if not site.root_page == home_page:
            site.root_page = home_page
            site.site_name = "Anupam Dutta Portfolio"
            site.save()

        # Typing texts
        typing_texts = [
            "Python Backend Engineer",
            "Generative AI Specialist",
            "LLM & RAG Engineer",
            "FastAPI Developer",
        ]
        for i, text in enumerate(typing_texts):
            HeroTypingText.objects.create(page=home_page, text=text, sort_order=i)

        # Social links
        social_links = [
            ("linkedin", "https://www.linkedin.com/in/kinganupamdutta/", "fab fa-linkedin-in", "LinkedIn"),
            ("github", "https://github.com/kinganupamdutta27/", "fab fa-github", "GitHub"),
            ("email", "mailto:anupamdutta27121998.in@gmail.com", "fas fa-envelope", "Email"),
        ]
        for i, (platform, url, icon, title) in enumerate(social_links):
            HeroSocialLink.objects.create(
                page=home_page, platform=platform, url=url,
                icon_class=icon, title=title, sort_order=i,
            )

        # About stats
        stats = [
            ("2+", "Years Experience"),
            ("10+", "Projects Completed"),
            ("6+", "Certifications"),
        ]
        for i, (number, label) in enumerate(stats):
            AboutStat.objects.create(page=home_page, number=number, label=label, sort_order=i)

        # Contact links
        contact_links = [
            ("email", "anupamdutta27121998.in@gmail.com", "mailto:anupamdutta27121998.in@gmail.com", "fas fa-envelope"),
            ("phone", "+91 9163142597", "tel:+919163142597", "fas fa-phone"),
            ("linkedin", "linkedin.com/in/kinganupamdutta", "https://www.linkedin.com/in/kinganupamdutta/", "fab fa-linkedin-in"),
            ("github", "github.com/kinganupamdutta27", "https://github.com/kinganupamdutta27/", "fab fa-github"),
        ]
        for i, (ctype, display, url, icon) in enumerate(contact_links):
            ContactLink.objects.create(
                page=home_page, contact_type=ctype, display_text=display,
                url=url, icon_class=icon, sort_order=i,
            )

        home_page.save_revision().publish()
        self.stdout.write(self.style.SUCCESS("  HomePage created with all sections."))

    def _seed_skills(self):
        """Seed skill categories and skills."""
        from apps.portfolio.models import SkillCategory, Skill

        if SkillCategory.objects.exists():
            self.stdout.write(self.style.WARNING("  Skills already exist. Skipping."))
            return

        self.stdout.write("Creating skills...")

        skills_data = [
            ("Programming Languages", "fas fa-code", [
                "Python", "Java", "JavaScript", "SQL", "C",
            ]),
            ("Backend Development", "fas fa-server", [
                "FastAPI", "Django", "Flask", "RESTful APIs", "SQLAlchemy",
                "JWT", "Microservices", "Stripe", "Payment Gateway Integration",
            ]),
            ("AI/ML & GenAI", "fas fa-robot", [
                "GPT-4", "LLM", "Llama", "MultiAgent AI", "RAG", "Agentic AI",
                "Prompt Engineering", "LangSmith", "HuggingFace", "OpenAI",
                "Pinecone", "LangGraph", "LangChain", "FAISS",
            ]),
            ("Databases & Caching", "fas fa-database", [
                "PostgreSQL", "MySQL", "MongoDB", "Redis", "SQLite",
            ]),
            ("DevOps & Cloud", "fas fa-cloud", [
                "Docker", "Git", "GitHub Actions", "AWS",
            ]),
            ("Integration", "fas fa-puzzle-piece", [
                "Software AG webMethods", "EDI Workflows", "Microservices",
            ]),
        ]

        for i, (name, icon, skills) in enumerate(skills_data):
            category = SkillCategory.objects.create(
                name=name, icon_class=icon, sort_order=i, is_active=True,
            )
            for j, skill_name in enumerate(skills):
                Skill.objects.create(category=category, name=skill_name, sort_order=j)

        self.stdout.write(self.style.SUCCESS(f"  {len(skills_data)} skill categories created."))

    def _seed_experience(self):
        """Seed work experience with highlights."""
        from apps.portfolio.models import Experience, ExperienceHighlight

        if Experience.objects.exists():
            self.stdout.write(self.style.WARNING("  Experience already exists. Skipping."))
            return

        self.stdout.write("Creating experience...")

        experiences_data = [
            {
                "job_title": "Jr. Python Developer",
                "company_name": "Weavers Web Solutions",
                "location": "Kolkata",
                "start_date": datetime.date(2025, 4, 1),
                "end_date": None,
                "is_current": True,
                "highlights": [
                    "Developed RAG systems using LangGraph and LangChain for context-aware response generation",
                    "Engineered GenAI applications using FastAPI, improving API response time by 45%",
                    "Built agentic RAG system using GPT-4.1, reducing token costs by 80%",
                    "Boosted OTP authentication performance by 70% with Redis caching",
                    "Integrated PostgreSQL with SQLAlchemy ORM for scalable data handling",
                ],
            },
            {
                "job_title": "Python Developer Intern",
                "company_name": "Weavers Web Solutions",
                "location": "Kolkata",
                "start_date": datetime.date(2024, 11, 1),
                "end_date": datetime.date(2025, 3, 31),
                "is_current": False,
                "highlights": [
                    "Contributed to scalable, production-ready APIs in microservices architecture",
                    "Reduced response latency by 35% in FastAPI-based microservices",
                    "Optimized data processing pipelines with 70% improvement in efficiency",
                    "Improved code coverage by 60% through unit tests and code reviews",
                ],
            },
            {
                "job_title": "Programmer Analyst Trainee",
                "company_name": "Cognizant",
                "location": "Kolkata",
                "start_date": datetime.date(2023, 12, 1),
                "end_date": datetime.date(2024, 10, 31),
                "is_current": False,
                "highlights": [
                    "Collaborated with cross-functional Agile teams on enterprise-grade applications",
                    "Developed and optimized EDI workflows using Software AG webMethods",
                    "Improved process efficiency by 70%",
                    "Utilized Java for backend development and SQL for data retrieval",
                ],
            },
        ]

        for i, exp_data in enumerate(experiences_data):
            highlights = exp_data.pop("highlights")
            exp = Experience.objects.create(sort_order=i, is_active=True, **exp_data)
            for j, text in enumerate(highlights):
                ExperienceHighlight.objects.create(experience=exp, text=text, sort_order=j)

        self.stdout.write(self.style.SUCCESS(f"  {len(experiences_data)} experience entries created."))

    def _seed_projects(self):
        """Seed projects with technologies."""
        from apps.portfolio.models import Project, ProjectTechnology

        if Project.objects.exists():
            self.stdout.write(self.style.WARNING("  Projects already exist. Skipping."))
            return

        self.stdout.write("Creating projects...")

        projects_data = [
            {
                "title": "Plugg - GenAI Matchmaking App",
                "description": "Modern matchmaking platform with AI-powered recommendations and real-time chat.",
                "live_url": "",
                "github_url": "",
                "technologies": ["Python", "Flask", "LangChain", "Pinecone", "MongoDB", "Docker", "GCP", "Redis", "LangGraph", "OpenAI", "LangSmith", "HuggingFace"],
            },
            {
                "title": "Plumloom - AI Evaluation Platform",
                "description": "Platform to compare and analyze performance of multiple LLMs like GPT-4, Gemini.",
                "live_url": "",
                "github_url": "",
                "technologies": ["Python", "FastAPI", "OpenAI", "PostgreSQL", "Stripe Payment Integration", "Redis", "Heroku", "Docker", "GCP"],
            },
            {
                "title": "CaseCreate - Legal Automation",
                "description": "Intelligent legal automation platform using GenAI for contract drafting.",
                "live_url": "https://case-create.com/",
                "github_url": "",
                "technologies": ["Django", "OpenAI", "PostgreSQL", "MongoDB", "AWS Lambda"],
            },
            {
                "title": "Stock Market Prediction",
                "description": "ML model to predict S&P 500 trends using Random Forest.",
                "live_url": "",
                "github_url": "https://github.com/kinganupamdutta27/stock-market-prediction-using-random-forest",
                "technologies": ["Python", "Scikit-learn", "XGBoost", "Pandas"],
            },
            {
                "title": "Sign Language Recognition",
                "description": "Published research on hand gesture recognition using ML. (Springer Publication)",
                "live_url": "https://link.springer.com/chapter/10.1007/978-981-99-1983-3_29",
                "github_url": "",
                "technologies": ["Python", "OpenCV", "TensorFlow", "Mediapipe"],
            },
            {
                "title": "IoT Water Level Monitor",
                "description": "Remote monitoring system with automated pump control using Blynk app.",
                "live_url": "",
                "github_url": "https://github.com/kinganupamdutta27/IOT-BASED-WATER-LEVEL-MONITORING-AND-CONTROL-SYSTEM",
                "technologies": ["NodeMCU", "Arduino", "IoT", "Blynk"],
            },
            {
                "title": "VoterMatch - Political Matchmaking",
                "description": "AI-powered platform matching voters with political candidates based on policy preferences.",
                "live_url": "",
                "github_url": "",
                "technologies": ["Python", "Django", "Wagtail CMS", "JavaScript", "Unfold - Admin Theme", "PostgreSQL"],
            },
        ]

        for i, proj_data in enumerate(projects_data):
            technologies = proj_data.pop("technologies")
            project = Project.objects.create(
                sort_order=i, is_featured=True, is_active=True, **proj_data,
            )
            for j, tech_name in enumerate(technologies):
                ProjectTechnology.objects.create(project=project, name=tech_name, sort_order=j)

        self.stdout.write(self.style.SUCCESS(f"  {len(projects_data)} projects created."))

    def _seed_education(self):
        """Seed education entries."""
        from apps.portfolio.models import Education

        if Education.objects.exists():
            self.stdout.write(self.style.WARNING("  Education already exists. Skipping."))
            return

        self.stdout.write("Creating education...")

        education_data = [
            {
                "degree": "B.Tech in Computer Science & Engineering",
                "institution": "JIS College of Engineering, Kalyani",
                "start_year": 2020,
                "end_year": 2023,
                "grade": "GPA: 8.85",
            },
            {
                "degree": "Diploma in Computer Science & Technology",
                "institution": "JIS School of Polytechnic, Kalyani",
                "start_year": 2017,
                "end_year": 2020,
                "grade": "GPA: 8.7",
            },
            {
                "degree": "Madhyamik (Secondary)",
                "institution": "Bedibhawan Rabitirtha Vidyalaya",
                "start_year": 2014,
                "end_year": 2015,
                "grade": "",
            },
        ]

        for i, edu_data in enumerate(education_data):
            Education.objects.create(sort_order=i, is_active=True, **edu_data)

        self.stdout.write(self.style.SUCCESS(f"  {len(education_data)} education entries created."))

    def _seed_certifications(self):
        """Seed certification entries."""
        from apps.portfolio.models import Certification

        if Certification.objects.exists():
            self.stdout.write(self.style.WARNING("  Certifications already exist. Skipping."))
            return

        self.stdout.write("Creating certifications...")

        certifications_data = [
            ("AWS Cloud Foundations", "Amazon Web Services", "fab fa-aws"),
            ("AWS ML Foundations", "Amazon Web Services", "fab fa-aws"),
            ("AWS Data Analytics", "Amazon Web Services", "fab fa-aws"),
            ("CCNA: Intro to Networks", "Cisco", "fas fa-network-wired"),
            ("Programming with Python", "Internshala", "fab fa-python"),
            ("Java (Basic)", "HackerRank", "fab fa-java"),
        ]

        for i, (name, issuer, icon) in enumerate(certifications_data):
            Certification.objects.create(
                name=name, issuer=issuer, icon_class=icon,
                sort_order=i, is_active=True,
            )

        self.stdout.write(self.style.SUCCESS(f"  {len(certifications_data)} certifications created."))

    def _seed_site_config(self):
        """Seed site configuration."""
        from apps.home.models import SiteConfiguration
        from wagtail.models import Site

        self.stdout.write("Configuring site settings...")

        site = Site.objects.filter(is_default_site=True).first()
        if not site:
            self.stdout.write(self.style.WARNING("  No default site found. Skipping config."))
            return

        config, created = SiteConfiguration.objects.get_or_create(
            site=site,
            defaults={
                "site_name": "Anupam Dutta",
                "site_tagline": "Python Backend Engineer & GenAI Specialist",
                "meta_description": (
                    "Anupam Dutta - Python Backend Engineer & Generative AI Specialist. "
                    "Expert in FastAPI, LangChain, LangGraph, and scalable backend development."
                ),
                "meta_keywords": (
                    "Python Developer, Backend Engineer, GenAI, LLM Engineer, FastAPI, LangChain"
                ),
                "footer_text": "Anupam Dutta. All Rights Reserved.",
            },
        )

        if created:
            self.stdout.write(self.style.SUCCESS("  Site configuration created."))
        else:
            self.stdout.write(self.style.WARNING("  Site configuration already exists."))
