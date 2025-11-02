# 🚀 Deploy Django Backend to PythonAnywhere - Complete Guide

## Overview

PythonAnywhere is perfect for Django apps. **$5/month** for Beginner plan, **$7/month** if you need PostgreSQL.

**What you'll need:**
- PythonAnywhere account (sign up at pythonanywhere.com)
- Your Django project (already have it!)
- 15-30 minutes

---

## Step 1: Sign Up for PythonAnywhere

1. Go to **https://www.pythonanywhere.com**
2. Click **"Pricing"** or **"Get Started"**
3. Choose **Beginner plan ($5/month)**
   - Or Hacker plan ($10/month) if you need more resources
4. Create account (email, password)
5. Verify email

---

## Step 2: Access Your Dashboard

After signup, you'll see:
- **Files** tab - for uploading files
- **Web** tab - for creating web apps
- **Databases** tab - for databases
- **Consoles** tab - for Bash/Python consoles

---

## Step 3: Upload Your Project Files

### Option A: Upload via Web Interface (Easiest)

1. Go to **Files** tab
2. Navigate to `/home/yourusername/`
3. Create folder: `route-monitor-backend` (or `rm-backend`)
4. Click **Upload a file**
5. Upload these files/folders:
   - `manage.py`
   - `requirements.txt`
   - `route_monitor/` (entire folder)
   - `routes/` (entire folder)
   - `check_db_and_migrate.py`
   - `.env` file (if you have one) - **IMPORTANT: Create this manually with secrets!**

**Note:** You can upload a ZIP file and extract it:
1. Zip your `rm-backend` folder (without `myenv`, `__pycache__`, `.git`)
2. Upload ZIP to PythonAnywhere
3. Extract it

### Option B: Clone from GitHub (Recommended)

If your code is on GitHub:

1. Go to **Consoles** tab
2. Click **Bash** (start a new console)
3. Navigate to home:
   ```bash
   cd ~
   ```
4. Clone your repo:
   ```bash
   git clone https://github.com/yourusername/your-repo.git route-monitor-backend
   cd route-monitor-backend
   ```

**This is easier and updates are simpler!**

---

## Step 4: Install Dependencies

1. Go to **Consoles** tab
2. Click **Bash**
3. Navigate to your project:
   ```bash
   cd ~/route-monitor-backend
   ```
4. Create virtual environment:
   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```
5. Install requirements:
   ```bash
   pip install --user -r requirements.txt
   ```

**Note:** PythonAnywhere uses `--user` flag to install packages

---

## Step 5: Set Up Database

### Option A: Use PostgreSQL Add-on (+$2/month = $7 total)

1. Go to **Databases** tab
2. Click **"PostgreSQL"** button
3. Choose **"Add a PostgreSQL database"**
4. It will create database and show credentials
5. Save these credentials!

### Option B: Use Free MySQL (Free = $5 total)

If you can migrate to MySQL:

1. Go to **Databases** tab
2. Click **"MySQL"**
3. Create a new database
4. Note the database name (usually `yourusername$routemonitor`)

**You'll need to update `settings.py` for MySQL - see Step 6**

---

## Step 6: Configure Settings

### Update `settings.py` for PythonAnywhere

1. Go to **Files** tab
2. Navigate to `~/route-monitor-backend/route_monitor/settings.py`
3. Edit the file (PythonAnywhere has built-in editor)

**For PostgreSQL (if using add-on):**

Add this at the top:
```python
import os
```

Update database section:
```python
# Database - PostgreSQL (if using add-on)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'your_db_name'),
        'USER': os.environ.get('DB_USER', 'your_db_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your_db_password'),
        'HOST': os.environ.get('DB_HOST', 'your-username.postgres.pythonanywhere-services.com'),
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}
```

**For MySQL (if using free option):**

Update database section:
```python
# Database - MySQL (free)
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('DB_NAME', 'yourusername$routemonitor'),
        'USER': os.environ.get('DB_USER', 'yourusername'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'your_mysql_password'),
        'HOST': os.environ.get('DB_HOST', 'yourusername.mysql.pythonanywhere-services.com'),
        'PORT': os.environ.get('DB_PORT', '3306'),
    }
}
```

**Update ALLOWED_HOSTS:**
```python
ALLOWED_HOSTS = [
    'yourusername.pythonanywhere.com',
    'www.yourusername.pythonanywhere.com',
]
```

Replace `yourusername` with your PythonAnywhere username!

---

## Step 7: Set Environment Variables

PythonAnywhere doesn't use `.env` files by default. Set variables in WSGI file or use bashrc.

### Method 1: Set in WSGI File (Recommended)

We'll do this in Step 8 when creating the web app.

### Method 2: Set in `.bashrc`

1. Go to **Files** tab
2. Open `~/.bashrc`
3. Add at the end:
   ```bash
   export DJANGO_SECRET_KEY='your-secret-key-here'
   export DB_NAME='your-db-name'
   export DB_USER='your-db-user'
   export DB_PASSWORD='your-db-password'
   export DB_HOST='your-host'
   export DEBUG='False'
   ```

---

## Step 8: Create Web App

1. Go to **Web** tab
2. Click **"Add a new web app"**
3. **Domain:** Choose `yourusername.pythonanywhere.com` (free subdomain)
4. **Python version:** Select **Python 3.12** (or latest available)
5. **Framework:** Select **Django**
6. **Python path:** Enter:
   ```
   /home/yourusername/route-monitor-backend
   ```
7. **WSGI file location:** PythonAnywhere will suggest:
   ```
   /var/www/yourusername_pythonanywhere_com_wsgi.py
   ```

Click **Next**.

---

## Step 9: Configure WSGI File

1. PythonAnywhere will open the WSGI file editor
2. **DELETE** all the default code
3. **REPLACE** with this:

```python
import os
import sys

# Add your project directory to path
path = '/home/yourusername/route-monitor-backend'
if path not in sys.path:
    sys.path.insert(0, path)

# Set environment variables
os.environ['DJANGO_SETTINGS_MODULE'] = 'route_monitor.settings'
os.environ['DJANGO_SECRET_KEY'] = 'your-secret-key-here'
os.environ['DEBUG'] = 'False'
os.environ['ALLOWED_HOSTS'] = 'yourusername.pythonanywhere.com'

# Database credentials (PostgreSQL)
os.environ['DB_NAME'] = 'your-db-name'
os.environ['DB_USER'] = 'your-db-user'
os.environ['DB_PASSWORD'] = 'your-db-password'
os.environ['DB_HOST'] = 'your-db-host'
os.environ['DB_PORT'] = '5432'

# For MySQL (if using free option), use:
# os.environ['DB_PORT'] = '3306'

# Activate virtual environment
activate_this = '/home/yourusername/route-monitor-backend/venv/bin/activate_this.py'
with open(activate_this) as f:
    exec(f.read(), {'__file__': activate_this})

# Django WSGI application
from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()
```

**Replace:**
- `yourusername` with your PythonAnywhere username (appears in top right)
- Database credentials with actual values
- Secret key (generate one if needed)

**To generate secret key:**
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

4. Click **Save**

---

## Step 10: Run Migrations

1. Go to **Consoles** tab
2. Click **Bash**
3. Activate virtual environment:
   ```bash
   cd ~/route-monitor-backend
   source venv/bin/activate
   ```
4. Set environment variables (for this session):
   ```bash
   export DJANGO_SECRET_KEY='your-secret-key'
   export DB_NAME='your-db-name'
   export DB_USER='your-db-user'
   export DB_PASSWORD='your-db-password'
   export DB_HOST='your-db-host'
   ```
5. Run migrations:
   ```bash
   python manage.py migrate
   ```
6. Create superuser (optional):
   ```bash
   python manage.py createsuperuser
   ```

---

## Step 11: Configure Static Files

1. In **Web** tab, find **Static files** section
2. Add static files mapping:
   - **URL:** `/static/`
   - **Directory:** `/home/yourusername/route-monitor-backend/staticfiles/`
3. Collect static files:
   ```bash
   cd ~/route-monitor-backend
   source venv/bin/activate
   python manage.py collectstatic
   ```

---

## Step 12: Reload Web App

1. Go to **Web** tab
2. Scroll to top
3. Click big green **"Reload"** button
4. Wait 10-20 seconds

---

## Step 13: Test Your API

1. Open browser
2. Go to: `https://yourusername.pythonanywhere.com/api/health/`
3. Should return:
   ```json
   {
     "status": "healthy",
     "timestamp": "...",
     "message": "Service is running"
   }
   ```

Test other endpoints:
- `https://yourusername.pythonanywhere.com/api/`
- `https://yourusername.pythonanywhere.com/admin/`

---

## Step 14: Update Frontend

Update your frontend to point to new backend:

**Update `rm-frontend/next.config.js`:**
```javascript
module.exports = {
  assetPrefix: '/',
  output: 'export',
  images: {
    unoptimized: true,
  },
  env: {
    API_URL: process.env.API_URL || 'https://yourusername.pythonanywhere.com/api',
  },
};
```

Or set environment variable in your frontend hosting (Vercel, etc.):
- Key: `API_URL`
- Value: `https://yourusername.pythonanywhere.com/api`

---

## 🔧 Troubleshooting

### Issue: "Module not found"
```bash
# Make sure packages are installed
cd ~/route-monitor-backend
source venv/bin/activate
pip install --user -r requirements.txt
```

### Issue: "Database connection error"
- Check credentials in WSGI file
- Verify database exists in **Databases** tab
- Test connection in Bash console

### Issue: "Static files not loading"
- Run `python manage.py collectstatic`
- Check static files path in **Web** tab matches your `STATIC_ROOT`

### Issue: "500 Internal Server Error"
1. Go to **Web** tab
2. Click **"Error log"** link
3. Check errors there
4. Common issues:
   - Missing environment variables
   - Wrong database credentials
   - Import errors

### Issue: "Can't import Django"
```bash
# Make sure virtual environment is activated in WSGI file
# Check Python path in WSGI file is correct
```

---

## 📝 PythonAnywhere Limitations

**Free Tier:**
- ✅ Perfect for testing
- ❌ Can't run scheduled tasks
- ❌ Limited resources

**Beginner ($5/month):**
- ✅ Can run scheduled tasks
- ✅ Enough for small-medium apps
- ✅ 512MB disk space

**Hacker ($10/month):**
- ✅ More disk space
- ✅ Better performance
- ✅ Multiple web apps

---

## 🎯 Quick Reference Commands

**Access Bash Console:**
- Go to **Consoles** tab → **Bash**

**Reload Web App:**
- Go to **Web** tab → Click **Reload** button

**View Logs:**
- Go to **Web** tab → Click **Error log**

**Update Code:**
- If using Git: `git pull` in Bash console
- If uploading: Upload new files via **Files** tab

---

## ✅ Deployment Checklist

- [ ] PythonAnywhere account created
- [ ] Project files uploaded/cloned
- [ ] Virtual environment created and dependencies installed
- [ ] Database created (PostgreSQL or MySQL)
- [ ] `settings.py` updated with database credentials
- [ ] `ALLOWED_HOSTS` updated
- [ ] WSGI file configured
- [ ] Environment variables set in WSGI file
- [ ] Migrations run successfully
- [ ] Static files collected
- [ ] Web app reloaded
- [ ] Health endpoint tested
- [ ] Frontend updated with new API URL

---

## 🎉 Success!

Your backend is now live at:
```
https://yourusername.pythonanywhere.com
```

API endpoints:
```
https://yourusername.pythonanywhere.com/api/
https://yourusername.pythonanywhere.com/api/health/
```

**Cost: $5/month (MySQL) or $7/month (PostgreSQL)**

Much cheaper than Fly.io! 🎊

