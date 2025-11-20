#!/usr/bin/env python3
"""
Working test setup for Student Loan Portal
"""

import os
import sys
import django
from datetime import date, timedelta
from decimal import Decimal

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loan_app.settings')
django.setup()

from users.models import StudentUser, FinancierUser
from loans.models import LoanApplication

def create_test_users():
    """Create test users"""
    print("Creating test users...")
    
    # Create test student 1
    try:
        student1, created = StudentUser.objects.get_or_create(
            email='student1@test.com',
            defaults={
                'first_name': 'Rahul',
                'last_name': 'Sharma',
                'student_id': 'STU001',
                'university': 'Test University',
                'gpa': Decimal('8.5'),
                'phone_number': '9876543210'
            }
        )
        if created:
            student1.set_password('testpass123')
            student1.save()
            print(f"Created student: {student1.get_full_name()}")
        else:
            print(f"Student exists: {student1.get_full_name()}")
    except Exception as e:
        print(f"Student 1 error: {e}")
    
    # Create test student 2
    try:
        student2, created = StudentUser.objects.get_or_create(
            email='student2@test.com',
            defaults={
                'first_name': 'Priya',
                'last_name': 'Patel',
                'student_id': 'STU002',
                'university': 'Test College',
                'gpa': Decimal('7.8'),
                'phone_number': '9876543211'
            }
        )
        if created:
            student2.set_password('testpass123')
            student2.save()
            print(f"Created student: {student2.get_full_name()}")
        else:
            print(f"Student exists: {student2.get_full_name()}")
    except Exception as e:
        print(f"Student 2 error: {e}")
    
    # Create test financier user
    try:
        financier_user, created = StudentUser.objects.get_or_create(
            email='financier@test.com',
            defaults={
                'first_name': 'Amit',
                'last_name': 'Kumar',
                'student_id': 'FIN001',
                'university': 'Finance Company',
                'gpa': Decimal('0.0'),
                'phone_number': '9876543212',
                'user_type': 'financier'
            }
        )
        if created:
            financier_user.set_password('testpass123')
            financier_user.save()
            print(f"Created financier user: {financier_user.get_full_name()}")
        else:
            print(f"Financier user exists: {financier_user.get_full_name()}")
    except Exception as e:
        print(f"Financier user error: {e}")
    
    # Create financier profile
    try:
        if financier_user:
            financier_profile, created = FinancierUser.objects.get_or_create(
                user=financier_user,
                defaults={
                    'financier_id': 'FIN001',
                    'company_name': 'Test Finance Company',
                    'investment_amount': Decimal('100000.00')
                }
            )
            if created:
                print(f"Created financier profile: {financier_profile}")
            else:
                print(f"Financier profile exists: {financier_profile}")
    except Exception as e:
        print(f"Financier profile error: {e}")
    
    # Create admin user
    try:
        admin, created = StudentUser.objects.get_or_create(
            email='admin@test.com',
            defaults={
                'first_name': 'Admin',
                'last_name': 'User',
                'student_id': 'ADMIN001',
                'university': 'Admin',
                'gpa': Decimal('10.0'),
                'phone_number': '9876543213',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('admin123')
            admin.save()
            print(f"Created admin: {admin.get_full_name()}")
        else:
            print(f"Admin exists: {admin.get_full_name()}")
    except Exception as e:
        print(f"Admin error: {e}")

def create_test_loans():
    """Create test loan applications"""
    print("\nCreating test loans...")
    
    try:
        student = StudentUser.objects.filter(email='student1@test.com').first()
        if student:
            # Loan 1 - Pending
            loan1, created = LoanApplication.objects.get_or_create(
                student=student,
                amount=50000,
                reason='Need loan for semester fees and course materials',
                defaults={
                    'status': 'Pending',
                    'repayment_due_date': date.today() + timedelta(days=365),
                    'interest_rate': Decimal('10.00')
                }
            )
            if created:
                print(f"Created loan: Rs.{loan1.amount} - {loan1.reason[:30]}...")
            
            # Loan 2 - Approved
            loan2, created = LoanApplication.objects.get_or_create(
                student=student,
                amount=25000,
                reason='Need loan for textbooks and study materials',
                defaults={
                    'status': 'Approved',
                    'repayment_due_date': date.today() + timedelta(days=365),
                    'interest_rate': Decimal('10.00')
                }
            )
            if created:
                print(f"Created loan: Rs.{loan2.amount} - {loan2.reason[:30]}...")
    except Exception as e:
        print(f"Loan creation error: {e}")

def print_credentials():
    """Print test credentials"""
    print("\n" + "="*60)
    print("TEST CREDENTIALS FOR USER TESTING")
    print("="*60)
    
    print("\nSTUDENT ACCOUNTS:")
    print("Email: student1@test.com | Password: testpass123 | Name: Rahul Sharma")
    print("Email: student2@test.com | Password: testpass123 | Name: Priya Patel")
    
    print("\nFINANCIER ACCOUNTS:")
    print("Email: financier@test.com | Password: testpass123 | Name: Amit Kumar")
    
    print("\nADMIN ACCOUNT:")
    print("Email: admin@test.com | Password: admin123 | Name: Admin User")
    
    print("\nTESTING URLS:")
    print("Local: http://localhost:8000")
    print("Network: http://YOUR_IP_ADDRESS:8000")
    
    print("\nTESTING FEATURES:")
    print("- User Registration & Login")
    print("- Loan Application Process")
    print("- Payment Methods (UPI, Bank Transfer)")
    print("- Withdrawal Requests")
    print("- Admin Management")
    print("- Mobile Responsive Design")
    print("- Multi-language Support")
    
    print("\n" + "="*60)

def main():
    """Main function"""
    print("Student Loan Portal - Test Setup")
    print("="*40)
    
    create_test_users()
    create_test_loans()
    print_credentials()
    
    print("\nNEXT STEPS:")
    print("1. Start server: python manage.py runserver 0.0.0.0:8000")
    print("2. Share URL with testers")
    print("3. Use the credentials above for testing")
    print("4. Collect feedback")
    print("5. Deploy when ready!")
    
    print("\nReady for testing!")

if __name__ == "__main__":
    main()
