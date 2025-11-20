#!/usr/bin/env python
import os, sys, django
sys.path.append('.')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'loan_app.settings')
django.setup()

from django.contrib.auth import get_user_model
User = get_user_model()

admin = User.objects.get(email='admin@test.com')
print(f'Email: {admin.email}')
print(f'Is staff: {admin.is_staff}')
print(f'Is superuser: {admin.is_superuser}')
print(f'Is active: {admin.is_active}')
pwd_check = admin.check_password('admin123')
print(f'Password check (admin123): {pwd_check}')

