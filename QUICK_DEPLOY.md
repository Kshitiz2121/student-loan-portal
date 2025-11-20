# ⚡ Quick Deploy Guide - 5 Minutes to Live!

## 🎯 Fastest Way: Render (Recommended)

### Step 1: Generate Secret Key
Run this command and save the output:
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### Step 2: Go to Render
1. Visit: **https://render.com**
2. Sign up with GitHub (free)
3. Click **"New +"** → **"Web Service"**

### Step 3: Connect Repository
- Connect: `Kshitiz2121/student-loan-portal`
- Branch: `main`

### Step 4: Configure
- **Name**: `student-loan-portal`
- **Build Command**: 
  ```
  pip install -r requirements.txt && python manage.py collectstatic --noinput
  ```
- **Start Command**: 
  ```
  gunicorn loan_app.wsgi:application
  ```

### Step 5: Add Database
1. Click **"New +"** → **"PostgreSQL"**
2. Name: `student-loan-portal-db`
3. Plan: **Free**
4. Copy the **Internal Database URL**

### Step 6: Set Environment Variables
In your Web Service → **Environment** tab, add:

```
SECRET_KEY=<paste-your-generated-secret-key>
DEBUG=False
ALLOWED_HOSTS=student-loan-portal.onrender.com
DATABASE_URL=<paste-internal-database-url-from-step-5>
```

### Step 7: Deploy!
Click **"Create Web Service"** and wait 5-10 minutes.

### Step 8: Run Migrations
After deployment, go to **Shell** and run:
```bash
python manage.py migrate
python manage.py createsuperuser
```

### ✅ Done!
Your app is live at: `https://student-loan-portal.onrender.com`

---

## 🔄 After Deployment

### Update Code
```bash
git add .
git commit -m "Your changes"
git push
```
Render will auto-deploy!

### View Logs
Render Dashboard → Your Service → **Logs** tab

### Update Environment Variables
Render Dashboard → Your Service → **Environment** tab

---

## 🆘 Troubleshooting

**App won't start?**
- Check **Logs** tab in Render
- Verify all environment variables are set

**Database errors?**
- Run migrations: `python manage.py migrate`
- Check DATABASE_URL is correct

**Static files not loading?**
- Build command includes `collectstatic`
- Check STATIC_ROOT in settings

---

**Need more details?** See `DEPLOY_LIVE.md` for complete guide.

