from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from decouple import config


class Command(BaseCommand):
    help = 'Create superuser from environment variables if not exists'

    def handle(self, *args, **kwargs):
        username = config('DJANGO_SUPERUSER_USERNAME', default='admin')
        email = config('DJANGO_SUPERUSER_EMAIL', default='admin@example.com')
        password = config('DJANGO_SUPERUSER_PASSWORD', default='admin123')

        if not User.objects.filter(username=username).exists():
            User.objects.create_superuser(username=username, email=email, password=password)
            self.stdout.write(self.style.SUCCESS(f'Superuser "{username}" created.'))
        else:
            self.stdout.write(f'Superuser "{username}" already exists.')
