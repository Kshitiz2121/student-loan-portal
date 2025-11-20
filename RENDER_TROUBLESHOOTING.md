# 🔧 Render Deployment Troubleshooting

## Common Issues and Solutions

### Issue: "Exited with status 1 while running your code"

This usually means the app started but crashed immediately. Check these:

#### 1. Check Your Environment Variables

Make sure ALL of these are set in Render:
- ✅ `SECRET_KEY` - Must be set!
- ✅ `DEBUG` - Set to `False` for production
- ✅ `ALLOWED_HOSTS` - Must include your Render URL (e.g., `student-loan-portal.onrender.com`)
- ✅ `DATABASE_URL` - Must be set to your PostgreSQL Internal Database URL

#### 2. Check Your Build Command

Should be:
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput
```

#### 3. Check Your Start Command

Should be:
```bash
gunicorn loan_app.wsgi:application
```

**NOT** `gunicorn app:app` ❌

#### 4. Check Pre-Deploy Command

Should be:
```bash
python manage.py migrate --noinput
```

#### 5. View Logs

1. Go to your Render service
2. Click on **"Logs"** tab
3. Look for error messages at the bottom

Common errors you might see:

**"ModuleNotFoundError"**
- Missing package in requirements.txt
- Solution: Add missing package to requirements.txt

**"Database connection failed"**
- DATABASE_URL is wrong or missing
- Solution: Check DATABASE_URL in environment variables

**"DisallowedHost"**
- ALLOWED_HOSTS doesn't include your Render URL
- Solution: Add your Render URL to ALLOWED_HOSTS

**"SECRET_KEY not set"**
- SECRET_KEY environment variable missing
- Solution: Add SECRET_KEY to environment variables

### How to Get Your Render URL

After creating the service, your URL will be:
```
https://student-loan-portal.onrender.com
```

(Replace `student-loan-portal` with your actual service name)

### Quick Fix Checklist

1. ✅ All environment variables set?
2. ✅ Start command is `gunicorn loan_app.wsgi:application`?
3. ✅ Build command includes `collectstatic`?
4. ✅ DATABASE_URL is the Internal Database URL (not External)?
5. ✅ ALLOWED_HOSTS includes your Render URL?

### Still Not Working?

1. **Check the Logs tab** - This shows the actual error
2. **Try Manual Deploy** - Sometimes auto-deploy has issues
3. **Check Database** - Make sure PostgreSQL database is created and running
4. **Verify Build Succeeded** - Check if build completed successfully before start

### Testing Locally

To test if your app works:
```bash
# Set environment variables
export SECRET_KEY="your-secret-key"
export DEBUG="False"
export ALLOWED_HOSTS="localhost"
export DATABASE_URL="your-database-url"

# Run
python manage.py collectstatic --noinput
python manage.py migrate
gunicorn loan_app.wsgi:application
```

If this works locally, the issue is with Render configuration.

