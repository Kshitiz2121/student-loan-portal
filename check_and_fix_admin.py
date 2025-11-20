#!/usr/bin/env python
"""
Script to check and fix admin@test.com account
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

def check_and_fix_admin():
    """Check and fix admin@test.com account"""
    try:
        # Check if admin exists
        admin = User.objects.filter(email='admin@test.com').first()
        
        if admin:
            print(f"✅ Admin account found: {admin.email}")
            print(f"   Current status:")
            print(f"   - Is staff: {admin.is_staff}")
            print(f"   - Is superuser: {admin.is_superuser}")
            print(f"   - Is active: {admin.is_active}")
            print(f"   - First name: {admin.first_name}")
            print(f"   - Last name: {admin.last_name}")
            
            # Fix if needed
            needs_fix = False
            if not admin.is_staff:
                admin.is_staff = True
                needs_fix = True
                print("\n   ⚠️  Setting is_staff = True")
            
            if not admin.is_superuser:
                admin.is_superuser = True
                needs_fix = True
                print("   ⚠️  Setting is_superuser = True")
            
            if not admin.is_active:
                admin.is_active = True
                needs_fix = True
                print("   ⚠️  Setting is_active = True")
            
            # Reset password
            admin.set_password('admin123')
            needs_fix = True
            print("   ⚠️  Resetting password to 'admin123'")
            
            if needs_fix:
                admin.save()
                print("\n✅ Admin account fixed!")
            else:
                print("\n✅ Admin account is already configured correctly!")
            
            print(f"\n📋 Login credentials:")
            print(f"   Email: {admin.email}")
            print(f"   Password: admin123")
            
        else:
            print("❌ Admin account not found! Creating new admin account...")
            
            # Try to find by student_id first
            admin = User.objects.filter(student_id='ADMIN001').first()
            
            if admin:
                print(f"⚠️  Found user with ADMIN001 student_id, updating to admin@test.com...")
                admin.email = 'admin@test.com'
                admin.first_name = 'Admin'
                admin.last_name = 'User'
                admin.university = 'Admin University'
                admin.gpa = 9.99
                admin.is_staff = True
                admin.is_superuser = True
                admin.is_active = True
                admin.set_password('admin123')
                admin.save()
                print(f"✅ Updated existing account to admin: {admin.email}")
            else:
                # Create admin account with unique student_id
                import random
                student_id = f'ADMIN{random.randint(1000, 9999)}'
                admin = User.objects.create_user(
                    email='admin@test.com',
                    password='admin123',
                    first_name='Admin',
                    last_name='User',
                    student_id=student_id,
                    university='Admin University',
                    gpa=9.99,
                    is_staff=True,
                    is_superuser=True,
                    is_active=True
                )
                print(f"✅ Created admin account: {admin.email}")
            
            print(f"\n📋 Login credentials:")
            print(f"   Email: {admin.email}")
            print(f"   Password: admin123")
            
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    check_and_fix_admin()

