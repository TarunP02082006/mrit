import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()
from django.db import connection

with connection.cursor() as cur:
    cur.execute("SELECT name, default_version, installed_version FROM pg_available_extensions WHERE name = 'vector';")
    row = cur.fetchone()
    print('pgvector extension in database:', row)

