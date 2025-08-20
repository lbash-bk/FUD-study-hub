# your_main_app/management/commands/create_superuser.py
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Creates a superuser automatically if it doesn\'t exist'

    def handle(self, *args, **options):
        User = get_user_model()
        admin_username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
        admin_email = os.environ.get('DJANGO_SUPERUSER_EMAIL')
        admin_password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

        if not admin_username or not admin_email or not admin_password:
            self.stdout.write(
                self.style.WARNING('Superuser credentials not set in environment variables. Skipping creation.')
            )
            return

        if not User.objects.filter(username=admin_username).exists():
            self.stdout.write(self.style.NOTICE('Creating superuser...'))
            User.objects.create_superuser(
                username=admin_username,
                email=admin_email,
                password=admin_password
            )
            self.stdout.write(self.style.SUCCESS('Superuser created successfully!'))
        else:
            self.stdout.write(self.style.WARNING('Superuser already exists. Skipping.'))