import os
import csv
from django.core.management.base import BaseCommand
from django.core.files import File
from accounts.models import CustomUser
from machines.models import Machine, Manual, DocumentChunk
from assistant.rag import index_manual

class Command(BaseCommand):
    help = "Initializes default users, registers machines from CSV, and indexes PDF manuals."

    def handle(self, *args, **options):
        self.stdout.write("Setting up Challenge Environment...")

        # 1. Create Default Users for all 3 Roles
        users_data = [
            ('admin', 'admin@example.com', 'adminpassword123', CustomUser.ROLE_ADMIN, True),
            ('engineer', 'engineer@example.com', 'engineerpassword123', CustomUser.ROLE_ENGINEER, False),
            ('supervisor', 'supervisor@example.com', 'supervisorpassword123', CustomUser.ROLE_SUPERVISOR, False),
        ]

        for username, email, password, role, is_super in users_data:
            user, created = CustomUser.objects.get_or_create(username=username, defaults={'email': email, 'role': role})
            user.role = role
            user.is_staff = is_super
            user.is_superuser = is_super
            user.set_password(password)
            user.save()
            action = "Created" if created else "Updated"
            self.stdout.write(f"  {action} user: {username} (Role: {role})")

        # 2. Register Machines & Manuals from machine_manual_index.csv
        csv_path = 'data/machine_manual_index.csv'
        manuals_dir = 'data/Manuals'

        if not os.path.exists(csv_path):
            self.stderr.write(f"Error: {csv_path} not found.")
            return

        with open(csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                machine_id = row['machine_id'].strip()
                model = row['model'].strip()
                machine_name = row['machine_name'].strip()
                doc_id = row['document_id'].strip()
                rev = row['revision'].strip()
                pdf_name = row['pdf_filename'].strip()

                machine, _ = Machine.objects.get_or_create(
                    machine_id=machine_id,
                    defaults={'model': model, 'machine_name': machine_name}
                )

                manual_path = os.path.join(manuals_dir, pdf_name)
                if not os.path.exists(manual_path):
                    self.stderr.write(f"  Warning: Manual file {manual_path} does not exist.")
                    continue

                manual, m_created = Manual.objects.get_or_create(
                    machine=machine,
                    document_id=doc_id,
                    revision=rev,
                    defaults={'filename': pdf_name}
                )

                # Save file to manual's pdf_file field
                with open(manual_path, 'rb') as pdf_f:
                    manual.pdf_file.save(pdf_name, File(pdf_f), save=True)

                self.stdout.write(f"  Registered manual {doc_id} Rev {rev} for {machine_id}")

                # 3. Index manual into DocumentChunks
                success, msg = index_manual(manual)
                self.stdout.write(f"    -> Indexing: {msg}")

        total_chunks = DocumentChunk.objects.count()
        self.stdout.write(self.style.SUCCESS(f"Challenge setup complete! Total chunks indexed: {total_chunks}"))

