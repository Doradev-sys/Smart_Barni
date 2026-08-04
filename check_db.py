import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.dev')
django.setup()

from django.db import connection

try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        db_version = cursor.fetchone()
    print("✅ Connected successfully to PostgreSQL!")
    print("Database version:", db_version[0])
    print("Database name:", connection.settings_dict['NAME'])
except Exception as e:
    print("❌ Connection failed.")
    print("Error:", e)