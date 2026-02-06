#!/usr/bin/env python
"""
Setup script for Meeting Bot Summarizer
Run this script to quickly set up the project
"""

import os
import sys
import django
from django.conf import settings
from django.core.management import call_command

# Set up Django settings
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'meeting_bot.settings')
django.setup()

def setup_project():
    """Run setup tasks"""
    print("=" * 60)
    print("Meeting Bot Summarizer - Setup")
    print("=" * 60)
    
    # Run migrations
    print("\n[1/3] Running database migrations...")
    try:
        call_command('migrate', verbosity=1)
        print("✓ Database migrations completed")
    except Exception as e:
        print(f"✗ Migration failed: {e}")
        return False
    
    # Create superuser
    print("\n[2/3] Creating superuser...")
    try:
        call_command('createsuperuser', interactive=True)
    except Exception as e:
        print(f"Note: Superuser creation skipped: {e}")
    
    # Collect static files
    print("\n[3/3] Collecting static files...")
    try:
        call_command('collectstatic', '--noinput', verbosity=1)
        print("✓ Static files collected")
    except Exception as e:
        print(f"Note: Static files collection skipped: {e}")
    
    print("\n" + "=" * 60)
    print("Setup Complete! 🎉")
    print("=" * 60)
    print("\nTo start the development server, run:")
    print("  python manage.py runserver")
    print("\nThen open your browser to:")
    print("  http://localhost:8000/")
    print("\nFor admin panel:")
    print("  http://localhost:8000/admin/")
    
    return True

if __name__ == '__main__':
    success = setup_project()
    sys.exit(0 if success else 1)
