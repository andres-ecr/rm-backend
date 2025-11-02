# PythonAnywhere-specific settings
# Add these to your route_monitor/settings.py or create this file and import it

import os

# Database configuration for PythonAnywhere
# Choose ONE: PostgreSQL (add-on) or MySQL (free)

# ============================================
# OPTION 1: PostgreSQL (Add-on, $2/month extra = $7 total)
# ============================================
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),  # Usually: yourusername.postgres.pythonanywhere-services.com
        'PORT': os.environ.get('DB_PORT', '5432'),
    }
}

# ============================================
# OPTION 2: MySQL (Free, included = $5 total)
# ============================================
# Uncomment this if using MySQL, comment out PostgreSQL above
# DATABASES = {
#     'default': {
#         'ENGINE': 'django.db.backends.mysql',
#         'NAME': os.environ.get('DB_NAME'),  # Usually: yourusername$routemonitor
#         'USER': os.environ.get('DB_USER'),  # Usually: yourusername
#         'PASSWORD': os.environ.get('DB_PASSWORD'),  # Set in PythonAnywhere Databases tab
#         'HOST': os.environ.get('DB_HOST', 'yourusername.mysql.pythonanywhere-services.com'),
#         'PORT': os.environ.get('DB_PORT', '3306'),
#         'OPTIONS': {
#             'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
#         }
#     }
# }

# Update ALLOWED_HOSTS for PythonAnywhere
# Replace 'yourusername' with your actual PythonAnywhere username
ALLOWED_HOSTS = [
    'yourusername.pythonanywhere.com',
    'www.yourusername.pythonanywhere.com',
    # Add your custom domain if you have one
]

# Static files configuration
STATIC_ROOT = '/home/yourusername/route-monitor-backend/staticfiles'
STATIC_URL = '/static/'

# Media files (if you use file uploads)
MEDIA_ROOT = '/home/yourusername/route-monitor-backend/media'
MEDIA_URL = '/media/'

# For MySQL, you'll also need to install mysqlclient
# Add to requirements.txt: mysqlclient==2.1.1
# Run: pip install --user mysqlclient

