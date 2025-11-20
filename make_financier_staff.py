#!/usr/bin/env python
"""
Script to make financier account a staff user
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loan_app.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def make_financier_staff():
    """Make financier@test.com a staff user"""
    try:
        financier = User.objects.get(email='financier@test.com')
        financier.is_staff = True
        financier.is_superuser = True
        financier.save()
        print("✅ Successfully made financier@test.com a staff user!")
        print(f"   Email: {financier.email}")
        print(f"   Staff: {financier.is_staff}")
        print(f"   Superuser: {financier.is_superuser}")
        print("\nYou can now access the admin panel at /admin/")
    except User.DoesNotExist:
        print("❌ Error: financier@test.com not found!")
    except Exception as e:
        print(f"❌ Error: {str(e)}")

if __name__ == '__main__':
    make_financier_staff()

