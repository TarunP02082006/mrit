from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser
from machines.models import Machine, Manual, DocumentChunk


class ManualDeleteTests(TestCase):
    def setUp(self):
        # 1. Users
        self.admin = CustomUser.objects.create_user(
            username='admin_del_test',
            password='adminpassword123',
            role=CustomUser.ROLE_ADMIN,
            is_staff=True
        )
        self.engineer = CustomUser.objects.create_user(
            username='engineer_del_test',
            password='engineerpassword123',
            role=CustomUser.ROLE_ENGINEER
        )
        self.supervisor = CustomUser.objects.create_user(
            username='supervisor_del_test',
            password='supervisorpassword123',
            role=CustomUser.ROLE_SUPERVISOR
        )

        # 2. Machine
        self.machine = Machine.objects.create(
            machine_id='M-TEST1',
            model='TEST-100',
            machine_name='Testing Machine'
        )

        # 3. Manuals
        self.manual_to_delete = Manual.objects.create(
            machine=self.machine,
            document_id='DOC-DEL-01',
            revision='1.0',
            filename='delete_me.pdf',
            is_indexed=True
        )
        self.manual_to_keep = Manual.objects.create(
            machine=self.machine,
            document_id='DOC-KEEP-02',
            revision='1.0',
            filename='keep_me.pdf',
            is_indexed=True
        )

        # 4. Chunks
        DocumentChunk.objects.create(
            manual=self.manual_to_delete,
            machine_id='M-TEST1',
            document_id='DOC-DEL-01',
            revision='1.0',
            page_number=1,
            section_title='DELETION TEST',
            chunk_text='This chunk should be removed.',
            chunk_index=0
        )
        DocumentChunk.objects.create(
            manual=self.manual_to_keep,
            machine_id='M-TEST1',
            document_id='DOC-KEEP-02',
            revision='1.0',
            page_number=1,
            section_title='RETENTION TEST',
            chunk_text='This chunk should remain.',
            chunk_index=0
        )

        self.client = APIClient()

    def test_admin_can_delete_manual(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('api-manual-delete', kwargs={'document_id': 'DOC-DEL-01'})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(resp.data.get('message'), "PDF manual deleted successfully.")

        # Verify manual record is deleted
        self.assertFalse(Manual.objects.filter(document_id='DOC-DEL-01').exists())
        # Verify associated chunks are deleted
        self.assertFalse(DocumentChunk.objects.filter(document_id='DOC-DEL-01').exists())

        # Verify other manual and its chunks remain untouched
        self.assertTrue(Manual.objects.filter(document_id='DOC-KEEP-02').exists())
        self.assertEqual(DocumentChunk.objects.filter(document_id='DOC-KEEP-02').count(), 1)

    def test_engineer_cannot_delete_manual(self):
        self.client.force_authenticate(user=self.engineer)
        url = reverse('api-manual-delete', kwargs={'document_id': 'DOC-DEL-01'})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        # Manual must still exist
        self.assertTrue(Manual.objects.filter(document_id='DOC-DEL-01').exists())
        self.assertEqual(DocumentChunk.objects.filter(document_id='DOC-DEL-01').count(), 1)

    def test_supervisor_cannot_delete_manual(self):
        self.client.force_authenticate(user=self.supervisor)
        url = reverse('api-manual-delete', kwargs={'document_id': 'DOC-DEL-01'})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_403_FORBIDDEN)
        # Manual must still exist
        self.assertTrue(Manual.objects.filter(document_id='DOC-DEL-01').exists())
        self.assertEqual(DocumentChunk.objects.filter(document_id='DOC-DEL-01').count(), 1)

    def test_unauthenticated_cannot_delete_manual(self):
        url = reverse('api-manual-delete', kwargs={'document_id': 'DOC-DEL-01'})
        resp = self.client.post(url)
        self.assertIn(resp.status_code, [status.HTTP_401_UNAUTHORIZED, status.HTTP_403_FORBIDDEN])
        self.assertTrue(Manual.objects.filter(document_id='DOC-DEL-01').exists())

    def test_delete_nonexistent_manual_returns_404(self):
        self.client.force_authenticate(user=self.admin)
        url = reverse('api-manual-delete', kwargs={'document_id': 'NONEXISTENT-99'})
        resp = self.client.post(url)
        self.assertEqual(resp.status_code, status.HTTP_404_NOT_FOUND)
