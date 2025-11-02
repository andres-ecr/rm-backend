#!/usr/bin/env python
"""
Script to check database connection before running migrations.
This prevents build failures when database is temporarily unavailable.
"""
import os
import sys
import time

# Setup Django before importing Django modules
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'route_monitor.settings')

import django
django.setup()

from django.db import connection
from django.core.management import call_command
from django.db.utils import OperationalError

def check_database_connection(max_retries=3, retry_delay=2):
    """Check if database connection is available with retries."""
    for attempt in range(1, max_retries + 1):
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                print(f"✅ Database connection successful (attempt {attempt})")
                return True
        except OperationalError as e:
            error_msg = str(e)
            print(f"⚠️  Database connection failed (attempt {attempt}/{max_retries}): {error_msg}")
            
            # Check if it's a hostname resolution error
            if "could not translate host name" in error_msg.lower() or "name or service not known" in error_msg.lower():
                print("⚠️  Hostname resolution error detected.")
                print("⚠️  This usually means:")
                print("   1. The database service doesn't exist or was deleted")
                print("   2. The DATABASE_URL environment variable is incorrect")
                print("   3. The database hostname changed")
                print("⚠️  Please check your database connection settings.")
            
            if attempt < max_retries:
                print(f"   Retrying in {retry_delay} seconds...")
                time.sleep(retry_delay)
            else:
                print("⚠️  All connection attempts failed.")
                return False
        except Exception as e:
            print(f"⚠️  Unexpected error checking database: {e}")
            return False
    
    return False

if __name__ == '__main__':
    # Debug: Show database connection info (without password)
    db_url = os.environ.get('DATABASE_URL', 'Not set')
    if db_url != 'Not set':
        # Mask password in URL for logging
        if '@' in db_url:
            parts = db_url.split('@')
            if '://' in parts[0]:
                auth_part = parts[0].split('://')[1]
                if ':' in auth_part:
                    user_pass = auth_part.split(':')
                    masked_url = db_url.replace(f":{user_pass[1]}@", ":****@", 1)
                    print(f"🔍 DATABASE_URL: {masked_url}")
                else:
                    print(f"🔍 DATABASE_URL: {db_url.split('@')[0]}@****")
            else:
                print("🔍 DATABASE_URL is set (password hidden)")
        else:
            print(f"🔍 DATABASE_URL: {db_url[:50]}...")
    else:
        print("⚠️  DATABASE_URL environment variable is not set!")
    
    if check_database_connection():
        print("✅ Running migrations...")
        try:
            call_command('migrate', verbosity=1, interactive=False)
            print("✅ Migrations completed successfully.")
            sys.exit(0)
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            print("⚠️  Build will continue, but migrations need to be run manually.")
            # Don't fail the build - allow service to start and run migrations manually
            sys.exit(0)
    else:
        print("⚠️  Skipping migrations during build.")
        print("⚠️  IMPORTANT: Migrations must be run manually or the service may not work correctly.")
        print("⚠️  You can run migrations manually: python manage.py migrate")
        sys.exit(0)  # Don't fail the build

