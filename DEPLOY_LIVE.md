# 🚀 How to Make Your Loan App Live - Step-by-Step Guide

This guide will help you deploy your Django loan application to a live server. We'll use **Render** (easiest and free) as the primary option, with alternatives.

## 🎯 Quick Start - Deploy to Render (Recommended - FREE)

Render is the easiest platform to deploy Django apps. It's free for hobby projects and automatically deploys from GitHub.

### Step 1: Prepare Your Code

Your code is already on GitHub! ✅

### Step 2: Update Settings for Production

We need to update `settings.py` to use environment variables. I'll help you with this.

### Step 3: Create Render Account

1. Go to: **https://render.com**
2. Sign up with your GitHub account (free)
3. Click **"New +"** → **"Web Service"**

### Step 4: Connect Your Repository

1. Click **"Connect GitHub"**
2. Authorize Render to access your repositories
3. Select: **`Kshitiz2121/student-loan-portal`**
4. Click **"Connect"**

### Step 5: Configure Your Service

Fill in these settings:

- **Name**: `student-loan-portal` (or any name)
- **Region**: Choose closest to you (e.g., `Singapore` or `Oregon`)
- **Branch**: `main`
- **Root Directory**: Leave empty (or `./` if needed)
- **Environment**: `Python 3`
- **Build Command**: 
  ```bash
  pip install -r requirements.txt && python manage.py collectstatic --noinput
  ```
- **Start Command**: 
  ```bash
  gunicorn loan_app.wsgi:application
  ```

### Step 6: Add Environment Variables

Click **"Advanced"** → **"Add Environment Variable"** and add:

```
SECRET_KEY=your-generated-secret-key-here
DEBUG=False
ALLOWED_HOSTS=your-app-name.onrender.com
DATABASE_URL=postgresql://... (Render will provide this)
```

**To generate SECRET_KEY:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 7: Add PostgreSQL Database

1. In Render dashboard, click **"New +"** → **"PostgreSQL"**
2. Name it: `student-loan-portal-db`
3. Choose **Free** plan
4. Copy the **Internal Database URL**
5. Go back to your Web Service
6. Add environment variable:
   - Key: `DATABASE_URL`
   - Value: Paste the Internal Database URL

### Step 8: Deploy!

1. Click **"Create Web Service"**
2. Render will automatically:
   - Clone your code
   - Install dependencies
   - Run migrations
   - Start your app
3. Wait 5-10 minutes for first deployment

### Step 9: Run Migrations

After deployment, go to **Shell** in Render dashboard and run:
```bash
python manage.py migrate
python manage.py createsuperuser
```

### Step 10: Your App is Live! 🎉

Your app will be available at:
```
https://your-app-name.onrender.com
```

---

## 🌐 Alternative: Railway (Also Easy & Free)

### Step 1: Sign Up
1. Go to: **https://railway.app**
2. Sign up with GitHub

### Step 2: New Project
1. Click **"New Project"**
2. Select **"Deploy from GitHub repo"**
3. Choose your repository

### Step 3: Add Database
1. Click **"+ New"** → **"Database"** → **"PostgreSQL"**
2. Railway automatically sets `DATABASE_URL`

### Step 4: Configure Environment Variables
Click on your service → **Variables** tab → Add:
- `SECRET_KEY`
- `DEBUG=False`
- `ALLOWED_HOSTS=*.railway.app`

### Step 5: Deploy
Railway auto-detects Django and deploys automatically!

---

## 🌐 Alternative: Heroku (Classic Option)

### Step 1: Install Heroku CLI
Download from: https://devcenter.heroku.com/articles/heroku-cli

### Step 2: Login
```bash
heroku login
```

### Step 3: Create App
```bash
heroku create your-app-name
```

### Step 4: Add PostgreSQL
```bash
heroku addons:create heroku-postgresql:hobby-dev
```

### Step 5: Set Environment Variables
```bash
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com
```

### Step 6: Deploy
```bash
git push heroku main
heroku run python manage.py migrate
heroku run python manage.py createsuperuser
```

---

## ⚙️ Required Settings Updates

Before deploying, we need to update `settings.py` to:
1. Use environment variables
2. Support production database
3. Configure static files properly

I'll help you update this in the next step.

---

## 📋 Post-Deployment Checklist

- [ ] App is accessible via URL
- [ ] Database migrations completed
- [ ] Superuser account created
- [ ] Can login to admin panel
- [ ] Static files loading (CSS, JS)
- [ ] User registration works
- [ ] Loan application works
- [ ] Email notifications work (if configured)

---

## 🔧 Troubleshooting

### App Won't Start
- Check build logs in Render/Railway dashboard
- Verify `requirements.txt` has all dependencies
- Check `Procfile` is correct

### Database Errors
- Verify `DATABASE_URL` is set correctly
- Run migrations: `python manage.py migrate`

### Static Files Not Loading
- Run: `python manage.py collectstatic --noinput`
- Check `STATIC_ROOT` in settings

### 500 Errors
- Check application logs
- Verify all environment variables are set
- Check `DEBUG=False` in production

---

## 💰 Cost Comparison

| Platform | Free Tier | Paid Plans Start At |
|----------|-----------|---------------------|
| **Render** | ✅ Yes (with limitations) | $7/month |
| **Railway** | ✅ Yes ($5 credit/month) | Pay as you go |
| **Heroku** | ❌ No (discontinued) | $5/month |

**Recommendation**: Start with **Render** - it's the easiest and has a good free tier!

---

## 🎯 Next Steps After Deployment

1. **Set up custom domain** (optional)
2. **Configure email** (Gmail SMTP or SendGrid)
3. **Set up payment gateways** (Razorpay, PayU)
4. **Enable SSL/HTTPS** (usually automatic)
5. **Set up monitoring** (Sentry for error tracking)
6. **Configure backups** (automated database backups)

---

**Need help?** Check the deployment logs in your platform's dashboard or refer to `PRODUCTION_SETUP_GUIDE.md` for detailed configuration.

