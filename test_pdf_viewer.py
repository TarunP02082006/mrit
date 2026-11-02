import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from rest_framework.test import APIClient
from rest_framework import status
from accounts.models import CustomUser

def test_viewer():
    print("=" * 60)
    print("VERIFYING PDF VIEWER ENDPOINT AND SECURITY HEADERS")
    print("=" * 60)

    client = APIClient()
    engineer = CustomUser.objects.get(username='engineer')
    client.force_authenticate(user=engineer)

    test_cases = [
        ('HP-MNT-01', 1),
        ('HP-MNT-01', 2),
        ('HP-MNT-01', 3),
        ('HP-OPS-01', 1),
        ('AC-OM-01', 1),
    ]

    for doc_id, page in test_cases:
        url = f'/api/manuals/{doc_id}/page/{page}/'
        res = client.get(url)

        print(f"\nTesting: {doc_id} (Page {page}) -> GET {url}")
        assert res.status_code == status.HTTP_200_OK, f"Failed with status {res.status_code}"
        print(f"  Status:               {res.status_code} OK")

        ct = res.headers.get('Content-Type')
        assert ct == 'application/pdf', f"Expected application/pdf, got {ct}"
        print(f"  Content-Type:         {ct}")

        cd = res.headers.get('Content-Disposition')
        assert 'inline' in cd, f"Expected inline disposition, got {cd}"
        print(f"  Content-Disposition:  {cd}")

        xfo = res.headers.get('X-Frame-Options')
        assert xfo == 'SAMEORIGIN', f"Expected SAMEORIGIN, got {xfo}"
        print(f"  X-Frame-Options:      {xfo}")

        # Verify PDF magic bytes
        pdf_bytes = b"".join(res.streaming_content) if hasattr(res, 'streaming_content') else res.content
        assert pdf_bytes.startswith(b'%PDF-'), "Response is not a valid PDF binary"
        print(f"  Binary Verification:  Valid PDF ({len(pdf_bytes)} bytes)")
        print(f"  --> PASS")

    print("\n" + "=" * 60)
    print("ALL PDF VIEWER TESTS PASSED SUCCESSFULLY!")
    print("=" * 60)

if __name__ == '__main__':
    test_viewer()

