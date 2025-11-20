# 🚀 Production Setup Guide

This guide will help you configure the Student Loan Portal for production deployment.

## 📋 Prerequisites

- Python 3.11+
- PostgreSQL database (or compatible)
- SMTP email server
- Payment gateway accounts (Razorpay, PayU, Paytm)
- Deployment platform account (Heroku, Railway, Render, etc.)
- Domain name (optional but recommended)

---

## 🔧 Step 1: Environment Variables Setup

### Create `.env` file (DO NOT commit to git)

```bash
# Copy the example file
cp env.example .env
```

### Required Environment Variables

```env
# Django Settings
SECRET_KEY=your-secure-secret-key-here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Database (PostgreSQL for production)
DATABASE_URL=postgresql://username:password@host:port/database_name

# Email Settings
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@yourdomain.com

# Payment Gateway Settings
RAZORPAY_KEY_ID=your_production_razorpay_key_id
RAZORPAY_KEY_SECRET=your_production_razorpay_secret
PAYU_MERCHANT_KEY=your_production_payu_merchant_key
PAYU_SALT=your_production_payu_salt
PAYTM_MERCHANT_ID=your_production_paytm_merchant_id
PAYTM_MERCHANT_KEY=your_production_paytm_merchant_key

# Application Settings
BASE_URL=https://yourdomain.com
```

### Generate Secure Secret Key

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

---

## 🔒 Step 2: Update Settings.py for Production

Update `loan_app/settings.py` to use environment variables:

```python
import os
from decouple import config

# Security
SECRET_KEY = config('SECRET_KEY', default='django-insecure-change-me')
DEBUG = config('DEBUG', default=False, cast=bool)
ALLOWED_HOSTS = config('ALLOWED_HOSTS', default='localhost').split(',')

# Database
import dj_database_url
DATABASES = {
    'default': dj_database_url.config(
        default=config('DATABASE_URL', default='sqlite:///db.sqlite3')
    )
}

# Email
EMAIL_BACKEND = config('EMAIL_BACKEND', default='django.core.mail.backends.console.EmailBackend')
EMAIL_HOST = config('EMAIL_HOST', default='')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@studentloanportal.com')

# Payment Gateways
RAZORPAY_KEY_ID = config('RAZORPAY_KEY_ID', default='')
RAZORPAY_KEY_SECRET = config('RAZORPAY_KEY_SECRET', default='')
PAYU_MERCHANT_KEY = config('PAYU_MERCHANT_KEY', default='')
PAYU_SALT = config('PAYU_SALT', default='')
PAYTM_MERCHANT_ID = config('PAYTM_MERCHANT_ID', default='')
PAYTM_MERCHANT_KEY = config('PAYTM_MERCHANT_KEY', default='')

# Application
BASE_URL = config('BASE_URL', default='http://localhost:8000')

# CORS (Production)
CORS_ALLOW_ALL_ORIGINS = False
CORS_ALLOWED_ORIGINS = [
    "https://yourdomain.com",
    "https://www.yourdomain.com",
]

# Security Headers
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

---

## 📧 Step 3: Email Configuration

### Option 1: Gmail SMTP

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password:
   - Go to Google Account settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"
3. Use the app password in `EMAIL_HOST_PASSWORD`

### Option 2: SendGrid

1. Sign up for SendGrid account
2. Create API key
3. Configure settings:
```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=your_sendgrid_api_key
```

### Option 3: AWS SES

1. Set up AWS SES
2. Verify your domain/email
3. Configure SMTP credentials

---

## 💳 Step 4: Payment Gateway Setup

### Razorpay

1. Sign up at https://razorpay.com
2. Get production API keys from dashboard
3. Set up webhooks for payment callbacks
4. Update `RAZORPAY_KEY_ID` and `RAZORPAY_KEY_SECRET`

### PayU

1. Sign up at https://payu.in
2. Get merchant key and salt
3. Configure callback URLs
4. Update `PAYU_MERCHANT_KEY` and `PAYU_SALT`

### Paytm

1. Sign up at https://paytm.com/business
2. Get merchant ID and key
3. Configure callback URLs
4. Update `PAYTM_MERCHANT_ID` and `PAYTM_MERCHANT_KEY`

---

## 🗄️ Step 5: Database Setup

### PostgreSQL (Recommended)

1. Install PostgreSQL or use cloud service (Heroku Postgres, AWS RDS, etc.)
2. Create database:
```sql
CREATE DATABASE student_loan_portal;
CREATE USER portal_user WITH PASSWORD 'secure_password';
GRANT ALL PRIVILEGES ON DATABASE student_loan_portal TO portal_user;
```

3. Update `DATABASE_URL` in `.env`:
```env
DATABASE_URL=postgresql://portal_user:secure_password@localhost:5432/student_loan_portal
```

4. Run migrations:
```bash
python manage.py migrate
```

---

## 📦 Step 6: Static Files Configuration

### Using WhiteNoise (Recommended for Heroku)

1. Add to `MIDDLEWARE` in `settings.py`:
```python
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',  # Add this
    # ... rest of middleware
]
```

2. Configure WhiteNoise:
```python
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

3. Collect static files:
```bash
python manage.py collectstatic --noinput
```

### Using CDN (Recommended for production)

1. Set up CDN (Cloudflare, AWS CloudFront, etc.)
2. Configure `STATIC_URL` to point to CDN
3. Upload static files to CDN

---

## 🚀 Step 7: Deployment

### Heroku

1. Install Heroku CLI
2. Login: `heroku login`
3. Create app: `heroku create your-app-name`
4. Set environment variables:
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
# ... set all other environment variables
```

5. Add PostgreSQL: `heroku addons:create heroku-postgresql:hobby-dev`
6. Deploy: `git push heroku main`
7. Run migrations: `heroku run python manage.py migrate`
8. Create superuser: `heroku run python manage.py createsuperuser`

### Railway

1. Install Railway CLI: `npm i -g @railway/cli`
2. Login: `railway login`
3. Initialize: `railway init`
4. Set environment variables in Railway dashboard
5. Deploy: `railway up`

### Render

1. Connect GitHub repository
2. Create new Web Service
3. Configure build and start commands
4. Set environment variables
5. Deploy

---

## 🔐 Step 8: Security Hardening

### SSL/HTTPS

1. Set up SSL certificate (Let's Encrypt, Cloudflare, etc.)
2. Enable HTTPS redirect in settings
3. Update `BASE_URL` to use HTTPS

### Security Headers

Add to `settings.py`:
```python
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### Database Backups

1. Set up automated backups
2. Test backup restoration
3. Store backups securely

---

## ✅ Step 9: Post-Deployment Checklist

- [ ] Verify all environment variables are set
- [ ] Run database migrations
- [ ] Collect static files
- [ ] Create superuser account
- [ ] Test user registration and login
- [ ] Test loan application flow
- [ ] Test payment processing
- [ ] Test email notifications
- [ ] Verify SSL/HTTPS is working
- [ ] Check security headers
- [ ] Test admin panel
- [ ] Verify static files are serving
- [ ] Test on mobile devices
- [ ] Check error logs
- [ ] Set up monitoring and alerts
- [ ] Configure backups

---

## 🐛 Troubleshooting

### Database Connection Issues

- Verify database credentials
- Check database is accessible from deployment platform
- Verify firewall rules

### Static Files Not Loading

- Run `collectstatic` command
- Check `STATIC_ROOT` and `STATIC_URL` settings
- Verify WhiteNoise or CDN configuration

### Email Not Sending

- Verify SMTP credentials
- Check email server allows connections
- Verify `DEFAULT_FROM_EMAIL` is set
- Check spam folder

### Payment Gateway Issues

- Verify API keys are correct
- Check webhook URLs are configured
- Verify callback URLs are accessible
- Check payment gateway logs

---

## 📞 Support

For issues or questions:
- Check Django documentation: https://docs.djangoproject.com/
- Check deployment platform documentation
- Review error logs
- Contact support team

---

**Last Updated**: January 2025

