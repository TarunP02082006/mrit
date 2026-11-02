import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.db import connection
from django.apps import apps
from django.core.management.color import no_style

def sync_database():
    print("=" * 60)
    print("SUPABASE POSTGRESQL SYNC & MIGRATION TOOL")
    print("=" * 60)

    vendor = connection.vendor
    host = connection.settings_dict.get('HOST', 'localhost')
    db_name = connection.settings_dict.get('NAME', 'postgres')
    user = connection.settings_dict.get('USER', 'postgres')

    print(f"Target Database: {db_name}")
    print(f"Host:            {host}")
    print(f"User:            {user}")
    print(f"Vendor:          {vendor}")

    if vendor != 'postgresql':
        print("\n[ERROR] Target database is not PostgreSQL. Please update your .env file.")
        return

    print("\n[Step 1/4] Testing connection to remote database...")
    try:
        with connection.cursor() as cur:
            cur.execute("SELECT version();")
            ver = cur.fetchone()[0]
            print(f"  Connected successfully! Database engine:")
            print(f"  {ver[:80]}...")
    except Exception as e:
        print(f"\n[FAILED] Could not connect to database: {e}")
        print("\nPlease check your credentials in .env (host, password, port, user).")
        return

    print("\n[Step 2/4] Applying Django database migrations...")
    call_command('migrate', interactive=False)
    print("  Migrations applied successfully.")

    fixture_file = 'datadump_utf8.json'
    if os.path.exists(fixture_file):
        print(f"\n[Step 3/4] Importing existing data from {fixture_file}...")
        try:
            call_command('loaddata', fixture_file)
            print("  Data imported successfully.")
        except Exception as e:
            print(f"  Warning during loaddata: {e}")
    else:
        print(f"\n[Step 3/4] Fixture {fixture_file} not found; running challenge seed...")
        call_command('setup_challenge')

    print("\n[Step 4/4] Synchronizing PostgreSQL auto-increment sequences...")
    try:
        models = [m for app in ['accounts', 'machines', 'history'] for m in apps.get_app_config(app).get_models()]
        sequence_sql = connection.ops.sequence_reset_sql(no_style(), models)
        with connection.cursor() as cursor:
            for sql in sequence_sql:
                cursor.execute(sql)
        print("  Sequences synchronized.")
    except Exception as e:
        print(f"  Note on sequence reset: {e}")

    print("\n" + "=" * 60)
    print("SYNC COMPLETE! Your Supabase database is ready to use!")
    print("=" * 60)

if __name__ == '__main__':
    sync_database()

