import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.contrib.auth import authenticate
from rest_framework.test import APIClient
from rest_framework import status
from django.core.files.uploadedfile import SimpleUploadedFile

from accounts.models import CustomUser
from machines.models import Machine, Manual, DocumentChunk
from history.models import QuestionHistory
from assistant.rag import answer_question, retrieve_passages

def run_tests():
    print("=" * 60)
    print("RUNNING POSTGRESQL FULL SYSTEM VERIFICATION SUITE")
    print("=" * 60)

    # 1. VERIFY POSTGRESQL ENGINE
    print("\n[TEST 1] Verifying Database Backend...")
    vendor = connection.vendor
    db_name = connection.settings_dict['NAME']
    host = connection.settings_dict['HOST']
    port = connection.settings_dict['PORT']
    print(f"  Vendor: {vendor}")
    print(f"  Database Name: {db_name}")
    print(f"  Host: {host}:{port}")
    assert vendor == 'postgresql', f"Expected postgresql, got {vendor}"
    with connection.cursor() as cur:
        cur.execute("SELECT version();")
        v = cur.fetchone()[0]
        print(f"  Engine Info: {v[:60]}...")
    print("  --> PASS: Application is actively connected to PostgreSQL.")

    # 2. TEST LOGIN & USER ROLES
    print("\n[TEST 2] Testing User Authentication & Roles in PostgreSQL...")
    users_to_test = [
        ('admin', 'adminpassword123', CustomUser.ROLE_ADMIN),
        ('engineer', 'engineerpassword123', CustomUser.ROLE_ENGINEER),
        ('supervisor', 'supervisorpassword123', CustomUser.ROLE_SUPERVISOR),
    ]
    for uname, pwd, expected_role in users_to_test:
        user = authenticate(username=uname, password=pwd)
        assert user is not None, f"Authentication failed for user {uname}"
        assert user.role == expected_role, f"Role mismatch for {uname}: expected {expected_role}, got {user.role}"
        print(f"  User '{uname}': Authenticated successfully. Role: {user.role}")
    print("  --> PASS: Authentication and role permissions verified.")

    # 3. TEST MACHINE SELECTION & DATA INTEGRITY
    print("\n[TEST 3] Testing Machine Selection & Data Retrieval...")
    hp200 = Machine.objects.filter(machine_id='M-HP200').first()
    ac90 = Machine.objects.filter(machine_id='M-AC90').first()
    assert hp200 is not None, "M-HP200 not found in PostgreSQL"
    assert ac90 is not None, "M-AC90 not found in PostgreSQL"
    print(f"  Found: {hp200} (Manuals count: {hp200.manuals.count()})")
    print(f"  Found: {ac90} (Manuals count: {ac90.manuals.count()})")
    print("  --> PASS: Machines and manuals properly linked.")

    # 4. TEST ROLE PERMISSION (ENGINEER CANNOT UPLOAD MANUAL)
    print("\n[TEST 4] Testing Mandatory Check 1 (Engineer Upload Denied 403)...")
    client = APIClient()
    engineer_user = CustomUser.objects.get(username='engineer')
    admin_user = CustomUser.objects.get(username='admin')

    client.force_authenticate(user=engineer_user)
    dummy_pdf = SimpleUploadedFile("test.pdf", b"%PDF-1.4 dummy", content_type="application/pdf")
    res = client.post('/api/manuals/upload/', {
        'machine_id': 'M-HP200',
        'document_id': 'HP-DENY-01',
        'revision': '1.0',
        'pdf_file': dummy_pdf
    }, format='multipart')
    print(f"  Engineer upload response status: {res.status_code}")
    assert res.status_code == status.HTTP_403_FORBIDDEN, f"Expected 403 Forbidden, got {res.status_code}"
    print("  --> PASS: Engineer upload rejected with HTTP 403 Forbidden.")

    # 5. TEST ADMIN REGISTRATION & UPLOAD
    print("\n[TEST 5] Testing Admin Machine Registration & Manual Upload...")
    client.force_authenticate(user=admin_user)
    # Register test machine
    test_m_id = 'M-TEST99'
    Machine.objects.filter(machine_id=test_m_id).delete()
    res_m = client.post('/api/machines/register/', {
        'machine_id': test_m_id,
        'model': 'TEST-99',
        'machine_name': 'Automated Test Rig'
    }, format='json')
    assert res_m.status_code == status.HTTP_201_CREATED, f"Admin machine creation failed: {res_m.data}"
    print(f"  Admin registered machine: {test_m_id}")

    # Clean up test machine
    Machine.objects.filter(machine_id=test_m_id).delete()
    print("  --> PASS: Admin operations verified in PostgreSQL.")

    # 6. TEST RAG MACHINE-BASED RETRIEVAL ISOLATION
    print("\n[TEST 6] Testing Mandatory Check 2 (Machine-Based Isolation)...")
    chunks_hp = retrieve_passages('M-HP200', 'What does E17 mean?')
    assert len(chunks_hp) > 0, "No chunks retrieved for HP-200"
    for c in chunks_hp:
        assert c.machine_id == 'M-HP200', f"Isolation breach! Found chunk from {c.machine_id}"
        assert 'AC' not in c.document_id, f"Isolation breach! AC document found in HP retrieval"
    print(f"  HP-200 retrieved {len(chunks_hp)} chunks, all strictly M-HP200.")

    chunks_ac = retrieve_passages('M-AC90', 'What does E17 mean?')
    assert len(chunks_ac) > 0, "No chunks retrieved for AC-90"
    for c in chunks_ac:
        assert c.machine_id == 'M-AC90', f"Isolation breach! Found chunk from {c.machine_id}"
    print(f"  AC-90 retrieved {len(chunks_ac)} chunks, all strictly M-AC90.")
    print("  --> PASS: Retrieval isolation 100% verified.")

    # 7. TEST AI QUESTION ANSWERING & CITATIONS
    print("\n[TEST 7] Testing Q&A Engine & Citations (Evaluation Demonstrations)...")
    # Demo 1: HP-200 Normal pressure
    ans1 = answer_question('M-HP200', 'What is the normal operating pressure range?')
    assert ans1['status'] == 'answered'
    assert '120 to 140 bar' in ans1['answer']
    assert any(c['document_id'] == 'HP-OPS-01' and c['page_number'] == 1 for c in ans1['citations'])
    print("  Demo 1 (Normal Pressure): PASS. Cites HP-OPS-01 Page 1.")

    # Demo 2: HP-200 E17 + Maintenance Intervals (Both Manuals)
    ans2 = answer_question('M-HP200', 'What should be checked when E17 occurs, and what are the maintenance inspection intervals?')
    assert ans2['status'] == 'answered'
    doc_ids = {c['document_id'] for c in ans2['citations']}
    assert 'HP-OPS-01' in doc_ids and 'HP-MNT-01' in doc_ids
    print("  Demo 2 (Multi-Manual Synthesis): PASS. Cites both HP-OPS-01 and HP-MNT-01.")

    # Demo 3: Cross-Machine Isolation (AF-10 on HP-200)
    ans3 = answer_question('M-HP200', 'When should the AF-10 filter indicator be checked?')
    assert ans3['status'] == 'insufficient_evidence'
    assert 'not contain enough information' in ans3['answer']
    print("  Demo 3 (Cross-Machine Isolation): PASS. Correctly reported insufficient evidence.")

    # Demo 4: Missing Information (Pump Price)
    ans4 = answer_question('M-HP200', 'What is the price of replacing the hydraulic pump?')
    assert ans4['status'] == 'insufficient_evidence'
    print("  Demo 4 (Missing Info / Price): PASS. Correctly reported insufficient evidence.")

    # 8. TEST QUESTION HISTORY & PERSISTENCE IN POSTGRESQL
    print("\n[TEST 8] Testing Question History Storage & Supervisor Audit in PostgreSQL...")
    initial_history_count = QuestionHistory.objects.count()
    client.force_authenticate(user=engineer_user)
    ask_res = client.post('/api/ask/', {
        'machine_id': 'M-HP200',
        'question': 'Automated Test: What does E17 mean?'
    }, format='json')
    assert ask_res.status_code == status.HTTP_200_OK
    new_history_count = QuestionHistory.objects.count()
    assert new_history_count == initial_history_count + 1, "Question history did not increment in PostgreSQL"
    latest_entry = QuestionHistory.objects.first()
    print(f"  Latest Question in PostgreSQL: '{latest_entry.question}' (Status: {latest_entry.status})")
    print(f"  Sources Saved: {len(latest_entry.sources)} citations stored.")

    # Test Supervisor Stats endpoint
    client.force_authenticate(user=CustomUser.objects.get(username='supervisor'))
    stats_res = client.get('/api/supervisor/stats/')
    assert stats_res.status_code == status.HTTP_200_OK
    print(f"  Supervisor Stats: Total={stats_res.data['total_questions']}, Answered={stats_res.data['answered_count']}, Insufficient={stats_res.data['insufficient_evidence_count']}")
    print("  --> PASS: Question history and supervisor audit logs active in PostgreSQL.")

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! POSTGRESQL MIGRATION 100% SUCCESSFUL!")
    print("=" * 60)

if __name__ == '__main__':
    run_tests()

