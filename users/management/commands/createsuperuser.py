from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()


class Command(BaseCommand):
    help = 'Create a superuser with required student fields'

    def add_arguments(self, parser):
        parser.add_argument('--email', type=str, required=True)
        parser.add_argument('--password', type=str, required=True)
        parser.add_argument('--first-name', type=str, required=True)
        parser.add_argument('--last-name', type=str, required=True)
        parser.add_argument('--student-id', type=str, required=True)
        parser.add_argument('--university', type=str, required=True)
        parser.add_argument('--gpa', type=float, required=True)

    def handle(self, *args, **options):
        try:
            with transaction.atomic():
                user = User.objects.create_user(
                    email=options['email'],
                    password=options['password'],
                    first_name=options['first_name'],
                    last_name=options['last_name'],
                    student_id=options['student_id'],
                    university=options['university'],
                    gpa=options['gpa'],
                    is_staff=True,
                    is_superuser=True,
                )
                
                self.stdout.write(
                    self.style.SUCCESS(
                        f'Successfully created superuser: {user.email}'
                    )
                )
                
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error creating superuser: {str(e)}')
            )
