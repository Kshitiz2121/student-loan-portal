#!/usr/bin/env python3
"""
Script to create test users for the Student Loan Portal
Run this script to quickly set up test accounts for user testing
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
    print("\n👨‍🎓 Creating test students...")
    
    # Test Student 1
    try:
        user1 = User.objects.create_user(
            username='test_student1',
            email='student1@test.com',
            password='testpass123',
            first_name='Rahul',
            last_name='Sharma'
        )
        student1 = StudentUser.objects.create(
            user=user1,
            student_id='STU001',
            phone='9876543210',
            college='Test University',
            course='Computer Science',
            year_of_study=3
        )
        print(f"✅ Created test student: {user1.get_full_name()} ({user1.username})")
    except Exception as e:
        print(f"⚠️  Student 1 already exists or error: {e}")
    
    # Test Student 2
    try:
        user2 = User.objects.create_user(
            username='test_student2',
            email='student2@test.com',
            password='testpass123',
            first_name='Priya',
            last_name='Patel'
        )
        student2 = StudentUser.objects.create(
            user=user2,
            student_id='STU002',
            phone='9876543211',
            college='Test College',
            course='Engineering',
            year_of_study=2
        )
        print(f"✅ Created test student: {user2.get_full_name()} ({user2.username})")
    except Exception as e:
        print(f"⚠️  Student 2 already exists or error: {e}")
    
    # Test Student 3
    try:
        user3 = User.objects.create_user(
            username='test_student3',
            email='student3@test.com',
            password='testpass123',
            first_name='Arjun',
            last_name='Singh'
        )
        student3 = StudentUser.objects.create(
            user=user3,
            student_id='STU003',
            phone='9876543212',
            college='Demo Institute',
            course='Business Administration',
            year_of_study=1
        )
        print(f"✅ Created test student: {user3.get_full_name()} ({user3.username})")
    except Exception as e:
        print(f"⚠️  Student 3 already exists or error: {e}")
    
    # Create test financiers
    print("\n💰 Creating test financiers...")
    
    # Test Financier 1
    try:
        user4 = User.objects.create_user(
            username='test_financier1',
            email='financier1@test.com',
            password='testpass123',
            first_name='Amit',
            last_name='Kumar'
        )
        financier1 = FinancierUser.objects.create(
            user=user4,
            financier_id='FIN001',
            phone='9876543213',
            company='Test Finance Company',
            investment_amount=100000
        )
        print(f"✅ Created test financier: {user4.get_full_name()} ({user4.username})")
    except Exception as e:
        print(f"⚠️  Financier 1 already exists or error: {e}")
    
    # Test Financier 2
    try:
        user5 = User.objects.create_user(
            username='test_financier2',
            email='financier2@test.com',
            password='testpass123',
            first_name='Sneha',
            last_name='Gupta'
        )
        financier2 = FinancierUser.objects.create(
            user=user5,
            financier_id='FIN002',
            phone='9876543214',
            company='Demo Investment Ltd',
            investment_amount=200000
        )
        print(f"✅ Created test financier: {user5.get_full_name()} ({user5.username})")
    except Exception as e:
        print(f"⚠️  Financier 2 already exists or error: {e}")
    
    # Create test loans
    print("\n📝 Creating test loan applications...")
    
    try:
        # Get first student
        student = StudentUser.objects.first()
        if student:
            # Loan 1 - Pending
            loan1 = LoanApplication.objects.create(
                student=student,
                amount=50000,
                purpose='Tuition Fees',
                description='Need loan for semester fees and course materials',
                status='Pending'
            )
            print(f"✅ Created test loan: ₹{loan1.amount} - {loan1.purpose}")
            
            # Loan 2 - Approved
            loan2 = LoanApplication.objects.create(
                student=student,
                amount=25000,
                purpose='Books and Supplies',
                description='Need loan for textbooks and study materials',
                status='Approved'
            )
            print(f"✅ Created test loan: ₹{loan2.amount} - {loan2.purpose}")
            
            # Loan 3 - Rejected
            loan3 = LoanApplication.objects.create(
                student=student,
                amount=100000,
                purpose='Laptop and Equipment',
                description='Need loan for laptop and other equipment',
                status='Rejected'
            )
            print(f"✅ Created test loan: ₹{loan3.amount} - {loan3.purpose}")
    
    except Exception as e:
        print(f"⚠️  Error creating test loans: {e}")
    
    print("\n🎉 Test users created successfully!")
    print_test_credentials()

def print_test_credentials():
    """Print test credentials for easy reference"""
    print("\n" + "="*60)
    print("📋 TEST CREDENTIALS FOR USER TESTING")
    print("="*60)
    
    print("\n👨‍🎓 STUDENT ACCOUNTS:")
    print("Username: test_student1 | Password: testpass123 | Name: Rahul Sharma")
    print("Username: test_student2 | Password: testpass123 | Name: Priya Patel")
    print("Username: test_student3 | Password: testpass123 | Name: Arjun Singh")
    
    print("\n💰 FINANCIER ACCOUNTS:")
    print("Username: test_financier1 | Password: testpass123 | Name: Amit Kumar")
    print("Username: test_financier2 | Password: testpass123 | Name: Sneha Gupta")
    
    print("\n👑 ADMIN ACCOUNT:")
    print("Username: admin | Password: admin123")
    
    print("\n🌐 TESTING URLS:")
    print("Local: http://localhost:8000")
    print("Network: http://YOUR_IP_ADDRESS:8000")
    print("Public: https://your-heroku-app.herokuapp.com")
    
    print("\n📱 TESTING FEATURES:")
    print("✅ User Registration & Login")
    print("✅ Loan Application Process")
    print("✅ Payment Methods (UPI, Bank Transfer)")
    print("✅ Withdrawal Requests")
    print("✅ Admin Management")
    print("✅ Mobile Responsive Design")
    print("✅ Multi-language Support")
    
    print("\n" + "="*60)

def create_admin_user():
    """Create admin user if it doesn't exist"""
    print("\n👑 Creating admin user...")
    
    try:
        admin_user = User.objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print(f"✅ Created admin user: {admin_user.username}")
    except Exception as e:
        print(f"⚠️  Admin user already exists or error: {e}")

def main():
    """Main function"""
    print("Student Loan Portal - Test User Setup")
    print("="*50)
    
    # Create admin user
    create_admin_user()
    
    # Create test users
    create_test_users()
    
    print("\n🎯 NEXT STEPS:")
    print("1. Start your server: python manage.py runserver 0.0.0.0:8000")
    print("2. Share the URL with testers")
    print("3. Share the test credentials above")
    print("4. Collect feedback from users")
    print("5. Deploy publicly when ready!")
    
    print("\n✨ Your Student Loan Portal is ready for testing!")

if __name__ == "__main__":
    main()
