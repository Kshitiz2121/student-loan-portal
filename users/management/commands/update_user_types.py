from django.core.management.base import BaseCommand
from users.models import StudentUser


class Command(BaseCommand):
    help = 'Update existing users with user_type field'

    def handle(self, *args, **options):
        # Update all existing users to be students by default
        updated_count = StudentUser.objects.filter(user_type__isnull=True).update(user_type='student')
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully updated {updated_count} users to have user_type="student"')
        )
