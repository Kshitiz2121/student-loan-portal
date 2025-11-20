#!/usr/bin/env python3
"""
Simple script to create test users for the Student Loan Portal
"""

import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loan_app.settings')
django.setup()

from django.contrib.auth.models import User
from users.models import StudentUser, FinancierUser
from loans.models import LoanApplication

def create_test_users():
    """Create test users for testing purposes"""
    print("Creating test users for Student Loan Portal...")
    
    # Create test students
    print("\nCreating test students...")
    
    # Test Student 1
    try:
        user1, created = User.objects.get_or_create(
            username='test_student1',
            defaults={
                'email': 'student1@test.com',
                'first_name': 'Rahul',
                'last_name': 'Sharma'
            }
        )
        if created:
            user1.set_password('testpass123')
            user1.save()
        
        student1, created = StudentUser.objects.get_or_create(
            user=user1,
            defaults={
                'student_id': 'STU001',
                'phone': '9876543210',
                'college': 'Test University',
                'course': 'Computer Science',
                'year_of_study': 3
            }
        )
        print(f"Student 1: {user1.get_full_name()} ({user1.username})")
    except Exception as e:
        print(f"Student 1 error: {e}")
    
    # Test Student 2
    try:
        user2, created = User.objects.get_or_create(
            username='test_student2',
            defaults={
                'email': 'student2@test.com',
                'first_name': 'Priya',
                'last_name': 'Patel'
            }
        )
        if created:
            user2.set_password('testpass123')
            user2.save()
        
        student2, created = StudentUser.objects.get_or_create(
            user=user2,
            defaults={
                'student_id': 'STU002',
                'phone': '9876543211',
                'college': 'Test College',
                'course': 'Engineering',
                'year_of_study': 2
            }
        )
        print(f"Student 2: {user2.get_full_name()} ({user2.username})")
    except Exception as e:
        print(f"Student 2 error: {e}")
    
    # Create test financiers
    print("\nCreating test financiers...")
    
    # Test Financier 1
    try:
        user3, created = User.objects.get_or_create(
            username='test_financier1',
            defaults={
                'email': 'financier1@test.com',
                'first_name': 'Amit',
                'last_name': 'Kumar'
            }
        )
        if created:
            user3.set_password('testpass123')
            user3.save()
        
        financier1, created = FinancierUser.objects.get_or_create(
            user=user3,
            defaults={
                'financier_id': 'FIN001',
                'phone': '9876543212',
                'company': 'Test Finance Company',
                'investment_amount': 100000
            }
        )
        print(f"Financier 1: {user3.get_full_name()} ({user3.username})")
    except Exception as e:
        print(f"Financier 1 error: {e}")
    
    # Create test loans
    print("\nCreating test loan applications...")
    
    try:
        student = StudentUser.objects.first()
        if student:
            # Loan 1 - Pending
            loan1, created = LoanApplication.objects.get_or_create(
                student=student,
                amount=50000,
                purpose='Tuition Fees',
                defaults={
                    'description': 'Need loan for semester fees and course materials',
                    'status': 'Pending'
                }
            )
            if created:
                print(f"Created loan: Rs.{loan1.amount} - {loan1.purpose}")
            
            # Loan 2 - Approved
            loan2, created = LoanApplication.objects.get_or_create(
                student=student,
                amount=25000,
                purpose='Books and Supplies',
                defaults={
                    'description': 'Need loan for textbooks and study materials',
                    'status': 'Approved'
                }
            )
            if created:
                print(f"Created loan: Rs.{loan2.amount} - {loan2.purpose}")
    
    except Exception as e:
        print(f"Error creating test loans: {e}")
    
    print("\nTest users created successfully!")
    print_test_credentials()

def print_test_credentials():
    """Print test credentials for easy reference"""
    print("\n" + "="*60)
    print("TEST CREDENTIALS FOR USER TESTING")
    print("="*60)
    
    print("\nSTUDENT ACCOUNTS:")
    print("Username: test_student1 | Password: testpass123 | Name: Rahul Sharma")
    print("Username: test_student2 | Password: testpass123 | Name: Priya Patel")
    
    print("\nFINANCIER ACCOUNTS:")
    print("Username: test_financier1 | Password: testpass123 | Name: Amit Kumar")
    
    print("\nADMIN ACCOUNT:")
    print("Username: admin | Password: admin123")
    
    print("\nTESTING URLS:")
    print("Local: http://localhost:8000")
    print("Network: http://YOUR_IP_ADDRESS:8000")
    
    print("\nTESTING FEATURES:")
    print("✓ User Registration & Login")
    print("✓ Loan Application Process")
    print("✓ Payment Methods (UPI, Bank Transfer)")
    print("✓ Withdrawal Requests")
    print("✓ Admin Management")
    print("✓ Mobile Responsive Design")
    print("✓ Multi-language Support")
    
    print("\n" + "="*60)

def create_admin_user():
    """Create admin user if it doesn't exist"""
    print("\nCreating admin user...")
    
    try:
        admin_user, created = User.objects.get_or_create(
            username='admin',
            defaults={
                'email': 'admin@test.com',
                'first_name': 'Admin',
                'last_name': 'User'
            }
        )
        if created:
            admin_user.set_password('admin123')
            admin_user.is_superuser = True
            admin_user.is_staff = True
            admin_user.save()
            print(f"Created admin user: {admin_user.username}")
        else:
            print(f"Admin user already exists: {admin_user.username}")
    except Exception as e:
        print(f"Admin user error: {e}")

def main():
    """Main function"""
    print("Student Loan Portal - Test User Setup")
    print("="*50)
    
    # Create admin user
    create_admin_user()
    
    # Create test users
    create_test_users()
    
    print("\nNEXT STEPS:")
    print("1. Start your server: python manage.py runserver 0.0.0.0:8000")
    print("2. Share the URL with testers")
    print("3. Share the test credentials above")
    print("4. Collect feedback from users")
    print("5. Deploy publicly when ready!")
    
    print("\nYour Student Loan Portal is ready for testing!")

if __name__ == "__main__":
    main()
