"""
Management command to set up production environment.
Creates superuser and seeds data automatically.
"""

import os

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.core.management.base import BaseCommand

User = get_user_model()


class Command(BaseCommand):
    help = "Set up production environment with superuser and seed data"

    def handle(self, *args, **options):
        # Create superuser from environment variables
        self.create_superuser()
        
        # Seed data
        self.seed_data()

    def create_superuser(self):
        """Create superuser from environment variables if not exists."""
        username = os.environ.get("DJANGO_SUPERUSER_USERNAME", "admin")
        email = os.environ.get("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
        password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

        if not password:
            self.stdout.write(
                self.style.WARNING(
                    "DJANGO_SUPERUSER_PASSWORD not set. Skipping superuser creation."
                )
            )
            return

        if User.objects.filter(username=username).exists():
            self.stdout.write(
                self.style.SUCCESS(f"Superuser '{username}' already exists.")
            )
            return

        User.objects.create_superuser(
            username=username,
            email=email,
            password=password,
        )
        self.stdout.write(
            self.style.SUCCESS(f"Superuser '{username}' created successfully!")
        )

    def seed_data(self):
        """Run seed_data command if HomePage doesn't exist."""
        from apps.home.models import HomePage

        if HomePage.objects.exists():
            self.stdout.write(
                self.style.SUCCESS("HomePage already exists. Skipping seed_data.")
            )
            return

        self.stdout.write(self.style.NOTICE("Seeding portfolio data..."))
        try:
            call_command("seed_data")
            self.stdout.write(
                self.style.SUCCESS("Portfolio data seeded successfully!")
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f"Error seeding data: {e}")
            )
