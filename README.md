# Anupam Dutta Portfolio

Production-ready portfolio and blog website built with **Django**, **Wagtail CMS**, and **Django Unfold** admin theme.

All content (projects, skills, experience, education, certifications, images, and more) is fully manageable through the Wagtail CMS admin interface — no code changes required.

---

## Table of Contents

- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Prerequisites](#prerequisites)
- [Getting Started — Local Development](#getting-started--local-development)
- [Getting Started — Docker](#getting-started--docker)
- [Accessing the Application](#accessing-the-application)
- [Content Management Guide](#content-management-guide)
- [Running Tests](#running-tests)
- [Management Commands](#management-commands)
- [Environment Variables](#environment-variables)
- [Production Deployment Checklist](#production-deployment-checklist)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Tech Stack

| Technology | Version | Purpose |
|---|---|---|
| **Django** | 5.1+ | Web framework |
| **Wagtail** | 6.3+ | Content Management System |
| **Django Unfold** | 0.40+ | Modern admin theme |
| **PostgreSQL** | 15+ | Production database |
| **SQLite** | — | Development database (zero setup) |
| **Redis** | 7+ | Caching (production) |
| **WhiteNoise** | 6+ | Static file serving |
| **Gunicorn** | 21+ | Production WSGI server |
| **Docker** | 24+ | Containerization |
| **Pytest** | 8+ | Testing framework |

---

## Project Structure

```
anupam-dutta-portfolio/
├── config/                         # Django project configuration
│   ├── settings/
│   │   ├── base.py                 # Shared/base settings
│   │   ├── development.py          # Development overrides (SQLite, DEBUG=True)
│   │   ├── production.py           # Production settings (PostgreSQL, Redis, security)
│   │   └── test.py                 # Test settings (in-memory SQLite, fast hashers)
│   ├── urls.py                     # Root URL routing
│   ├── wsgi.py                     # WSGI entry point
│   └── asgi.py                     # ASGI entry point
│
├── apps/
│   ├── core/                       # Shared utilities, middleware, template tags
│   │   ├── middleware.py            # Exception logging, request timing
│   │   ├── context_processors.py   # Global template context
│   │   ├── utils.py                # Helper functions
│   │   ├── views.py                # Custom 404/500 error pages
│   │   └── templatetags/           # Custom template tags & filters
│   │
│   ├── home/                       # HomePage (Wagtail Page model), Site Configuration
│   │   ├── models.py               # HomePage, SiteConfiguration, Orderables
│   │   ├── management/commands/    # seed_data management command
│   │   └── tests/                  # Model & view tests
│   │
│   ├── portfolio/                  # Skills, Experience, Projects, Education, Certs
│   │   ├── models.py               # Wagtail Snippets (all portfolio content)
│   │   ├── wagtail_hooks.py        # Snippet ViewSets for admin customization
│   │   └── tests/                  # Model tests
│   │
│   ├── contact/                    # AJAX contact form with rate limiting & spam protection
│   │   ├── models.py               # ContactSubmission model
│   │   ├── forms.py                # ContactForm with validation & spam checks
│   │   ├── views.py                # AJAX endpoint (JSON responses)
│   │   ├── admin.py                # Unfold admin for contact submissions
│   │   └── tests/                  # Form, model & view tests
│   │
│   └── blog/                       # Blog with Wagtail StreamField (expandable)
│       └── models.py               # BlogIndexPage, BlogPage
│
├── templates/                      # Django/Wagtail templates
│   ├── base.html                   # Base template (SEO, fonts, styles)
│   ├── home/home_page.html         # Main portfolio page
│   ├── includes/                   # Section partials (navbar, hero, about, etc.)
│   ├── blog/                       # Blog templates
│   ├── 404.html                    # Custom 404 page
│   └── 500.html                    # Custom 500 page (standalone HTML)
│
├── static/                         # CSS, JavaScript, static assets
│   ├── css/                        # style.css, components.css, sections.css
│   └── js/                         # main.js, particles.js
│
├── images/                         # Portfolio images (profile, projects)
├── requirements/                   # Pip requirements
│   ├── base.txt                    # Core dependencies
│   ├── development.txt             # Dev tools (debug toolbar, linters, pytest)
│   ├── production.txt              # Production (psycopg, redis, sentry)
│   └── test.txt                    # Test dependencies (pytest, factory-boy)
│
├── manage.py                       # Django management entry point
├── conftest.py                     # Global pytest fixtures
├── pytest.ini                      # Pytest configuration
├── Dockerfile                      # Multi-stage production Docker build
├── docker-compose.yml              # Docker Compose (PostgreSQL + Redis + Django)
├── .env.example                    # Example environment variables
├── .env                            # Local environment variables (not committed)
└── .gitignore                      # Git ignore rules
```

---

## Prerequisites

### For Local Development

- **Python 3.11+** — [Download](https://www.python.org/downloads/)
- **pip** — comes with Python
- **Git** — [Download](https://git-scm.com/)

### For Docker Deployment

- **Docker Desktop** — [Download](https://www.docker.com/products/docker-desktop/)
- **Docker Compose** — included with Docker Desktop

---

## Getting Started — Local Development

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd anupam-dutta-portfolio
```

### Step 2: Create a Virtual Environment

**Windows (PowerShell):**
```powershell
python -m venv venv
.\venv\Scripts\Activate
```

**macOS / Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements/development.txt
```

### Step 4: Configure Environment Variables

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

> The default values in `.env.example` work out-of-the-box for local development (SQLite, DEBUG=True).

### Step 5: Run Database Migrations

```bash
python manage.py migrate
```

### Step 6: Seed Portfolio Data

```bash
python manage.py seed_data
```

This populates the database with all portfolio content extracted from the original site:
- Hero section (name, greeting, typing texts, social links)
- About section (description, statistics)
- Skills (categories and individual skills)
- Work experience (with highlights)
- Projects (with technologies, links, images)
- Education
- Certifications
- Contact information
- Site configuration (SEO, footer text)

### Step 7: Create a Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to set up your admin username, email, and password.

### Step 8: Collect Static Files

```bash
python manage.py collectstatic --noinput
```

### Step 9: Start the Development Server

```bash
python manage.py runserver
```

The server starts at `http://127.0.0.1:8000/`.

---

## Getting Started — Docker

### Step 1: Configure Environment Variables

```bash
# Windows
copy .env.example .env

# macOS / Linux
cp .env.example .env
```

Edit `.env` and update these values for Docker/production:
```env
DJANGO_SETTINGS_MODULE=config.settings.production
SECRET_KEY=your-strong-secret-key-here
DATABASE_URL=postgres://portfolio_user:portfolio_pass@db:5432/portfolio_db
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

### Step 2: Build and Start Containers

```bash
docker-compose up --build -d
```

This starts three services:
| Service | Description | Port |
|---|---|---|
| `db` | PostgreSQL 15 database | 5432 |
| `redis` | Redis 7 cache | 6379 |
| `web` | Django application | 8000 |

### Step 3: Run Migrations Inside the Container

```bash
docker-compose exec web python manage.py migrate
```

### Step 4: Seed Data and Create Superuser

```bash
docker-compose exec web python manage.py seed_data
docker-compose exec web python manage.py createsuperuser
```

### Step 5: Verify

Open `http://localhost:8000/` in your browser.

### Docker Useful Commands

```bash
# View logs
docker-compose logs -f web

# Stop all containers
docker-compose down

# Stop and remove volumes (resets database)
docker-compose down -v

# Rebuild after code changes
docker-compose up --build -d

# Run a management command
docker-compose exec web python manage.py <command>

# Open a shell inside the container
docker-compose exec web bash
```

---

## Accessing the Application

| URL | Purpose | Login Required |
|---|---|---|
| `http://localhost:8000/` | Portfolio website (public) | No |
| `http://localhost:8000/cms/` | Wagtail CMS admin | Yes |
| `http://localhost:8000/admin/` | Django Admin (Unfold theme) | Yes |

### Wagtail CMS (`/cms/`)

This is the primary interface for managing all portfolio content:

- **Pages** → Edit HomePage sections (hero, about, contact details)
- **Snippets** → Manage Skills, Experience, Projects, Education, Certifications
- **Images** → Upload and manage portfolio and project images
- **Documents** → Upload downloadable files (resume, etc.)
- **Settings** → Site Configuration (site name, SEO meta, Google Analytics, footer)

### Django Admin (`/admin/`)

Uses the Unfold modern theme for:

- **Contact Submissions** → View, read/unread, and manage messages from the contact form
- **Users & Groups** → Authentication and permission management

---

## Content Management Guide

### Adding a New Project

1. Go to **Wagtail CMS** → **Snippets** → **Projects**
2. Click **"Add Project"**
3. Fill in: title, slug, description
4. Upload a project image
5. Add technologies (inline panel — click "Add Technology")
6. Set Live URL and/or GitHub URL
7. Toggle **Is Featured** and **Is Active**
8. Set **Sort Order** for display position
9. Click **Save**

### Adding a New Skill Category

1. Go to **Wagtail CMS** → **Snippets** → **Skill Categories**
2. Click **"Add Skill Category"**
3. Enter category name and Font Awesome icon class (e.g., `fas fa-code`)
4. Add individual skills (inline panel — click "Add Skill")
5. Each skill has a name, proficiency level (0–100), and icon class
6. Click **Save**

### Adding Work Experience

1. Go to **Wagtail CMS** → **Snippets** → **Experiences**
2. Click **"Add Experience"**
3. Fill in: job title, company name, start/end dates
4. Toggle **Is Current** if it's your current position
5. Add highlights/bullet points (inline panel)
6. Click **Save**

### Editing the Hero Section

1. Go to **Wagtail CMS** → **Pages** → **Home**
2. In the **Hero Section** tab, edit:
   - Tag text, greeting, name
   - Primary/Secondary CTA text and URLs
3. Expand **Hero Typing Texts** to add/edit rotating subtitle texts
4. Expand **Hero Social Links** to add/edit social media links
5. Click **Publish**

### Editing the About Section

1. Go to **Wagtail CMS** → **Pages** → **Home**
2. In the **About Section** tab, edit:
   - About image, description, resume URL
3. Expand **About Stats** to add/edit statistics (e.g., "5+ Years Experience")
4. Click **Publish**

### Editing Section Headers

1. Go to **Wagtail CMS** → **Pages** → **Home**
2. Each section has three fields:
   - **Label** (small text above title, e.g., "What I Do")
   - **Title** (main heading, e.g., "My")
   - **Title Highlight** (colored portion, e.g., "Skills")
3. Click **Publish**

### Toggling Section Visibility

1. Go to **Wagtail CMS** → **Pages** → **Home** → **Settings** tab
2. Toggle any section on/off:
   - Show Skills, Show Experience, Show Projects, Show Education, Show Certifications, Show Contact
3. Click **Publish**

### Managing Contact Submissions

1. Go to **Django Admin** (`/admin/`) → **Contact Submissions**
2. View all messages with sender name, email, date, and read status
3. Use bulk actions: **Mark as Read** / **Mark as Unread**
4. Click a submission to view the full message

---

## Running Tests

The project includes **74 tests** covering models, forms, and views across all apps.

### Run All Tests

```bash
pytest
```

### Run with Verbose Output

```bash
pytest -v
```

### Run with Short Traceback

```bash
pytest --tb=short -q
```

### Run Specific App Tests

```bash
pytest apps/home/tests/           # Home app tests (23 tests)
pytest apps/portfolio/tests/      # Portfolio app tests (27 tests)
pytest apps/contact/tests/        # Contact app tests (24 tests)
```

### Run a Specific Test File

```bash
pytest apps/contact/tests/test_forms.py
pytest apps/home/tests/test_models.py
```

### Run a Specific Test Class or Method

```bash
pytest apps/contact/tests/test_forms.py::TestContactForm
pytest apps/contact/tests/test_forms.py::TestContactForm::test_valid_form
```

### Run with Coverage Report

```bash
pytest --cov=apps --cov-report=html
```

Open `htmlcov/index.html` in a browser to view the coverage report.

---

## Management Commands

| Command | Description |
|---|---|
| `python manage.py runserver` | Start development server |
| `python manage.py migrate` | Apply database migrations |
| `python manage.py makemigrations` | Create new migrations after model changes |
| `python manage.py createsuperuser` | Create an admin user |
| `python manage.py seed_data` | Populate database with portfolio content |
| `python manage.py seed_data --flush` | Delete all existing data, then re-seed |
| `python manage.py collectstatic --noinput` | Collect static files for production |
| `python manage.py shell` | Open Django interactive shell |

---

## Environment Variables

All environment variables are managed via the `.env` file. See `.env.example` for the full list.

### Key Variables

| Variable | Default | Description |
|---|---|---|
| `DJANGO_SETTINGS_MODULE` | `config.settings.development` | Settings module to use |
| `SECRET_KEY` | (generated) | Django secret key — **change in production** |
| `DEBUG` | `True` | Debug mode — **set to False in production** |
| `ALLOWED_HOSTS` | `localhost,127.0.0.1` | Comma-separated allowed hostnames |
| `DATABASE_URL` | `sqlite:///db.sqlite3` | Database connection string |
| `REDIS_URL` | — | Redis connection string (production only) |
| `WAGTAIL_SITE_NAME` | `Anupam Dutta Portfolio` | Site name shown in Wagtail admin |
| `WAGTAILADMIN_BASE_URL` | `http://localhost:8000` | Base URL for Wagtail admin links |
| `EMAIL_HOST` | — | SMTP server for email (production) |
| `EMAIL_HOST_USER` | — | SMTP username |
| `EMAIL_HOST_PASSWORD` | — | SMTP password |
| `SENTRY_DSN` | — | Sentry error tracking DSN (production) |
| `CSRF_TRUSTED_ORIGINS` | `http://localhost:8000` | Trusted origins for CSRF |

---

## Production Deployment Checklist

- [ ] Set `DJANGO_SETTINGS_MODULE=config.settings.production`
- [ ] Set `DEBUG=False`
- [ ] Generate and set a strong `SECRET_KEY`
- [ ] Configure `ALLOWED_HOSTS` with your domain
- [ ] Set up PostgreSQL and configure `DATABASE_URL`
- [ ] Set up Redis and configure `REDIS_URL`
- [ ] Configure SMTP email settings for contact form notifications
- [ ] Set `CSRF_TRUSTED_ORIGINS` with your domain (e.g., `https://yourdomain.com`)
- [ ] Configure SSL/HTTPS (handled automatically in production settings)
- [ ] Run `python manage.py collectstatic --noinput`
- [ ] Run `python manage.py migrate`
- [ ] Create a superuser account
- [ ] Set up Sentry for error monitoring (`SENTRY_DSN`)
- [ ] Configure database backup strategy
- [ ] Configure media file storage (consider S3 for production)
- [ ] Set up a reverse proxy (Nginx) in front of Gunicorn

---

## Troubleshooting

### "The slug 'home' is already in use"

This happens when Wagtail's default "Welcome" page exists. The `seed_data` command handles this automatically, but if you encounter it:

```bash
python manage.py seed_data --flush
```

### Static files not loading

```bash
python manage.py collectstatic --noinput
```

For development, ensure `DEBUG=True` in your `.env` file.

### Database errors after model changes

```bash
python manage.py makemigrations
python manage.py migrate
```

### Port 8000 already in use

```bash
# Use a different port
python manage.py runserver 8080
```

### Docker container won't start

```bash
# Check logs
docker-compose logs -f web

# Rebuild from scratch
docker-compose down -v
docker-compose up --build -d
```

### Tests failing with slug errors

Ensure `conftest.py` has the latest version that handles default Wagtail page cleanup. Run:

```bash
pytest --tb=long -v
```

---

## License

GNU General Public License v3.0
