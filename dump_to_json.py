import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

with open('datadump_utf8.json', 'w', encoding='utf-8') as f:
    call_command(
        'dumpdata',
        '--natural-foreign',
        '--natural-primary',
        '-e', 'contenttypes',
        '-e', 'auth.Permission',
        indent=4,
        stdout=f
    )

print("Successfully dumped data to datadump_utf8.json with UTF-8 encoding!")

