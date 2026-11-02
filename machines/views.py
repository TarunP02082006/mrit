import os
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status, permissions
from django.shortcuts import get_object_or_404
from django.http import FileResponse, Http404

from machines.models import Machine, Manual
from machines.serializers import MachineSerializer, ManualSerializer
from accounts.permissions import IsAdminUserRole
from assistant.rag import index_manual

class MachineListAPIView(APIView):
    """
    GET: List all registered machines
    POST: Register a new machine (Admin only)
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        machines = Machine.objects.all()
        serializer = MachineSerializer(machines, many=True)
        return Response(serializer.data)

    def post(self, request):
        if not request.user.is_admin_role():
            return Response(
                {"error": "Forbidden: Only Administrators have permission to register machines."},
                status=status.HTTP_403_FORBIDDEN
            )
        serializer = MachineSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ManualUploadAPIView(APIView):
    """
    Upload a manual PDF.
    STRICT SECURITY REQUIREMENT:
    Only Administrators can upload manuals.
    Engineers and Supervisors receive HTTP 403 Forbidden.
    """
    permission_classes = [IsAdminUserRole]

    def post(self, request):
        machine_id = request.data.get('machine_id')
        document_id = request.data.get('document_id')
        revision = request.data.get('revision', '1.0')
        pdf_file = request.FILES.get('pdf_file')

        if not machine_id or not document_id:
            return Response(
                {"error": "machine_id and document_id are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        machine = get_object_or_404(Machine, machine_id=machine_id)

        manual, created = Manual.objects.get_or_create(
            machine=machine,
            document_id=document_id,
            revision=revision,
            defaults={
                'filename': pdf_file.name if pdf_file else f"{document_id}.pdf"
            }
        )

        if pdf_file:
            manual.pdf_file = pdf_file
            manual.filename = pdf_file.name
            manual.save()

        # Re-index chunks
        if manual.pdf_file:
            success, msg = index_manual(manual)
        else:
            msg = "Manual created without PDF file."

        return Response({
            "message": "Manual uploaded and indexed successfully.",
            "manual": ManualSerializer(manual).data,
            "indexing_result": msg
        }, status=status.HTTP_201_CREATED)


class ManualListAPIView(APIView):
    """
    GET: List all registered manuals
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        machine_id = request.query_params.get('machine_id')
        if machine_id:
            manuals = Manual.objects.filter(machine__machine_id=machine_id)
        else:
            manuals = Manual.objects.all()
        serializer = ManualSerializer(manuals, many=True)
        return Response(serializer.data)


class ServeManualFileAPIView(APIView):
    """
    Serves the PDF file for a given document ID or manual ID.
    Supports inline browser viewing so citations can open the PDF.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, document_id, page=None, *args, **kwargs):
        manual = get_object_or_404(Manual, document_id=document_id)
        if not manual.pdf_file or not os.path.exists(manual.pdf_file.path):
            raise Http404("PDF file not found.")
            
        page_num = page or request.query_params.get('page', '1')
        response = FileResponse(open(manual.pdf_file.path, 'rb'), content_type='application/pdf')
        response['Content-Disposition'] = f'inline; filename="{manual.filename}"'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        return response


class ManualDeleteAPIView(APIView):
    """
    POST / DELETE: Delete a manual, its physical PDF file, and associated document chunks.
    STRICT SECURITY REQUIREMENT:
    Only Administrators can delete manuals.
    Engineers and Supervisors receive HTTP 403 Forbidden.
    """
    permission_classes = [IsAdminUserRole]

    def post(self, request, document_id=None, *args, **kwargs):
        if not (request.user and request.user.is_authenticated and request.user.is_admin_role()):
            return Response(
                {"error": "Forbidden: Only Administrators have permission to delete manuals."},
                status=status.HTTP_403_FORBIDDEN
            )

        target_id = document_id or request.data.get('document_id')
        if not target_id:
            return Response(
                {"error": "document_id is required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        manual = Manual.objects.filter(document_id=target_id).first()
        if not manual and str(target_id).isdigit():
            manual = Manual.objects.filter(id=int(target_id)).first()

        if not manual:
            return Response(
                {"error": f"Manual with document ID '{target_id}' not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        try:
            # 1. Delete physical PDF file safely from disk
            if manual.pdf_file:
                try:
                    file_path = manual.pdf_file.path
                    if os.path.isfile(file_path):
                        os.remove(file_path)
                except Exception:
                    pass
                try:
                    manual.pdf_file.delete(save=False)
                except Exception:
                    pass

            # 2. Delete associated chunks
            manual.chunks.all().delete()

            # 3. Delete database record
            manual.delete()

            return Response({
                "message": "PDF manual deleted successfully.",
                "document_id": target_id
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response(
                {"error": f"Failed to delete manual: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def delete(self, request, document_id=None, *args, **kwargs):
        return self.post(request, document_id, *args, **kwargs)
