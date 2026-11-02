from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from machines.models import Machine, Manual, DocumentChunk
from assistant.rag import answer_question, retrieve_passages

class MandatoryChallengeTests(TestCase):
    def setUp(self):
        # 1. Create Users
        self.admin = CustomUser.objects.create_user(
            username='admin_test',
            password='adminpassword123',
            role=CustomUser.ROLE_ADMIN,
            is_staff=True
        )
        self.engineer = CustomUser.objects.create_user(
            username='engineer_test',
            password='engineerpassword123',
            role=CustomUser.ROLE_ENGINEER
        )
        self.supervisor = CustomUser.objects.create_user(
            username='supervisor_test',
            password='supervisorpassword123',
            role=CustomUser.ROLE_SUPERVISOR
        )

        # 2. Create Machines
        self.hp200 = Machine.objects.create(
            machine_id='M-HP200',
            model='HP-200',
            machine_name='Hydraulic forming press'
        )
        self.ac90 = Machine.objects.create(
            machine_id='M-AC90',
            model='AC-90',
            machine_name='Air compressor'
        )

        # 3. Create Manuals
        self.manual_hp_ops = Manual.objects.create(
            machine=self.hp200,
            document_id='HP-OPS-01',
            revision='1.0',
            filename='HP200_Operations_Rev1_0.pdf',
            is_indexed=True
        )
        self.manual_hp_mnt = Manual.objects.create(
            machine=self.hp200,
            document_id='HP-MNT-01',
            revision='1.0',
            filename='HP200_Maintenance_Rev1_0.pdf',
            is_indexed=True
        )
        self.manual_ac_om = Manual.objects.create(
            machine=self.ac90,
            document_id='AC-OM-01',
            revision='1.0',
            filename='AC90_Operations_Maintenance_Rev1_0.pdf',
            is_indexed=True
        )

        # 4. Create Document Chunks for HP-200 Operations
        DocumentChunk.objects.create(
            manual=self.manual_hp_ops,
            machine_id='M-HP200',
            document_id='HP-OPS-01',
            revision='1.0',
            page_number=1,
            section_title='OPERATING REFERENCE VALUES',
            chunk_text='Normal hydraulic pressure is 120 to 140 bar during the forming stage. Low-pressure trigger threshold: Below 110 bar for more than 5 seconds.',
            chunk_index=0
        )
        DocumentChunk.objects.create(
            manual=self.manual_hp_ops,
            machine_id='M-HP200',
            document_id='HP-OPS-01',
            revision='1.0',
            page_number=2,
            section_title='ALARM CODES REFERENCE',
            chunk_text='E17 indicates low hydraulic pressure when pressure remains below 110 bar for > 5 seconds during FORMING. Hold cycle and record pressure.',
            chunk_index=1
        )

        # 5. Create Document Chunks for HP-200 Maintenance
        DocumentChunk.objects.create(
            manual=self.manual_hp_mnt,
            machine_id='M-HP200',
            document_id='HP-MNT-01',
            revision='1.0',
            page_number=2,
            section_title='SCHEDULED INSPECTION INTERVALS',
            chunk_text='Every 50 operating hours check RF-20 restriction indicator. Every 500 operating hours planned RF-20 replacement. Every 2,000 hours or 12 months replace H46 oil.',
            chunk_index=0
        )
        DocumentChunk.objects.create(
            manual=self.manual_hp_mnt,
            machine_id='M-HP200',
            document_id='HP-MNT-01',
            revision='1.0',
            page_number=3,
            section_title='E17 TROUBLESHOOTING OBSERVATIONS',
            chunk_text='When E17 occurs collect observations: 1. Reservoir level, 2. Visible leakage, 3. RF-20 restriction indicator, 4. Oil temperature and pressure.',
            chunk_index=1
        )

        # 6. Create Document Chunks for AC-90
        DocumentChunk.objects.create(
            manual=self.manual_ac_om,
            machine_id='M-AC90',
            document_id='AC-OM-01',
            revision='1.0',
            page_number=2,
            section_title='ALARM CODES REFERENCE',
            chunk_text='E17 indicates high discharge temperature on AC-90 air compressor. Normal 70-90°C. Warning above 95°C. Stop 105°C.',
            chunk_index=0
        )
        DocumentChunk.objects.create(
            manual=self.manual_ac_om,
            machine_id='M-AC90',
            document_id='AC-OM-01',
            revision='1.0',
            page_number=3,
            section_title='MAINTENANCE SCHEDULE',
            chunk_text='Check AF-10 inlet-filter indicator every 100 operating hours. Planned replacement every 600 operating hours.',
            chunk_index=1
        )

        self.client = APIClient()

    def test_mandatory_check_1_engineer_cannot_upload_manual(self):
        """
        MANDATORY TEST 1:
        Only Administrators can upload manuals.
        When an Engineer attempts to upload, the backend must return HTTP 403 Forbidden.
        """
        self.client.force_authenticate(user=self.engineer)
        upload_url = reverse('api-manual-upload')
        
        payload = {
            'machine_id': 'M-HP200',
            'document_id': 'HP-TEST-01',
            'revision': '1.0',
        }
        response = self.client.post(upload_url, payload, format='multipart')
        
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN, 
                         "Engineer MUST receive 403 Forbidden when attempting to upload a manual.")

    def test_mandatory_check_2_machine_based_retrieval_isolation(self):
        """
        MANDATORY TEST 2:
        Retrieval must exclude another machine.
        When HP-200 is selected and question 'What does E17 mean?' is queried:
        - Retrieved passages MUST be strictly from M-HP200 (HP-OPS-01 / HP-MNT-01)
        - NO AC-90 (AC-OM-01) chunks must be retrieved!
        """
        retrieved = retrieve_passages('M-HP200', 'What does E17 mean?')
        
        # Verify all retrieved chunks belong strictly to M-HP200
        for chunk in retrieved:
            self.assertEqual(chunk.machine_id, 'M-HP200')
            self.assertNotEqual(chunk.machine_id, 'M-AC90')
            self.assertNotEqual(chunk.document_id, 'AC-OM-01')

        # Test AC-90 retrieval isolation
        retrieved_ac = retrieve_passages('M-AC90', 'What does E17 mean?')
        for chunk in retrieved_ac:
            self.assertEqual(chunk.machine_id, 'M-AC90')
            self.assertNotEqual(chunk.machine_id, 'M-HP200')

    def test_demo_1_supported_question(self):
        """
        Demonstration 1: HP-200 normal operating pressure range
        """
        res = answer_question('M-HP200', 'What is the normal operating pressure range?')
        self.assertEqual(res['status'], 'answered')
        self.assertIn('120 to 140 bar', res['answer'])
        
        # Check citations contain HP-OPS-01 page 1
        page_1_cited = any(c['document_id'] == 'HP-OPS-01' and c['page_number'] == 1 for c in res['citations'])
        self.assertTrue(page_1_cited, "Should cite HP-OPS-01 page 1")

    def test_demo_2_multi_manual_synthesis(self):
        """
        Demonstration 2: Question requiring two HP-200 manuals (E17 checks and intervals)
        """
        res = answer_question('M-HP200', 'What should be checked when E17 occurs, and what are the maintenance inspection intervals?')
        self.assertEqual(res['status'], 'answered')
        self.assertIn('RF-20', res['answer'])
        self.assertIn('50 operating hours', res['answer'])
        
        doc_ids = {c['document_id'] for c in res['citations']}
        self.assertIn('HP-OPS-01', doc_ids)
        self.assertIn('HP-MNT-01', doc_ids)

    def test_demo_3_cross_machine_isolation(self):
        """
        Demonstration 3: Asking HP-200 about AF-10 filter (belongs to AC-90)
        Must return insufficient evidence and not mix AC-90.
        """
        res = answer_question('M-HP200', 'When should the AF-10 filter indicator be checked?')
        self.assertEqual(res['status'], 'insufficient_evidence')
        self.assertIn('not contain enough information', res['answer'])
        self.assertIn('AF-10', res['answer'])

    def test_demo_4_missing_information(self):
        """
        Demonstration 4: Asking about pump replacement price
        Must return insufficient evidence without hallucinating.
        """
        res = answer_question('M-HP200', 'What is the price of replacing the hydraulic pump?')
        self.assertEqual(res['status'], 'insufficient_evidence')
        self.assertIn('not contain enough information', res['answer'])
