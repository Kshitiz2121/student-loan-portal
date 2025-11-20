#!/usr/bin/env python
import os
import sys
import django
from decimal import Decimal

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loan_app.settings')
django.setup()

from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

def create_superuser():
    try:
        with transaction.atomic():
            # Check if superuser already exists
            if User.objects.filter(is_superuser=True).exists():
                print("Superuser already exists!")
                return
            
            # Create superuser using the proper method for custom user model
            user = User.objects.create_superuser(
                email='admin@example.com',
                password='admin123',
                first_name='Admin',
                last_name='User',
                student_id='ADMIN001',
                university='Admin University',
                gpa=Decimal('9.99'),
            )
            
            print(f"Successfully created superuser: {user.email}")
            print("Email: admin@example.com")
            print("Password: admin123")
            
    except Exception as e:
        print(f"Error creating superuser: {str(e)}")

if __name__ == '__main__':
    create_superuser()
