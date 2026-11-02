from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import permissions
from django.db.models import Count

from history.models import QuestionHistory
from history.serializers import QuestionHistorySerializer
from accounts.permissions import IsSupervisorUserRole

class QuestionHistoryListAPIView(APIView):
    """
    List question history.
    Engineers see their questions; Admins and Supervisors can see all or filter.
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        user = request.user
        queryset = QuestionHistory.objects.all()

        if user.is_engineer_role() and not user.is_admin_role():
            queryset = queryset.filter(user=user)

        machine_id = request.query_params.get('machine_id')
        if machine_id:
            queryset = queryset.filter(machine__machine_id=machine_id)

        status_param = request.query_params.get('status')
        if status_param:
            queryset = queryset.filter(status=status_param)

        serializer = QuestionHistorySerializer(queryset[:100], many=True)
        return Response(serializer.data)


class SupervisorStatsAPIView(APIView):
    """
    Returns audit statistics for the Supervisor Dashboard:
    - Total questions asked
    - Count answered vs insufficient evidence
    - Breakdown per machine
    """
    permission_classes = [IsSupervisorUserRole]

    def get(self, request):
        total = QuestionHistory.objects.count()
        answered = QuestionHistory.objects.filter(status='answered').count()
        insufficient = QuestionHistory.objects.filter(status='insufficient_evidence').count()
        error = QuestionHistory.objects.filter(status='error').count()

        machine_stats = (
            QuestionHistory.objects.values('machine__machine_id', 'machine__model')
            .annotate(total=Count('id'))
            .order_by('-total')
        )

        unanswered_questions = (
            QuestionHistory.objects.filter(status='insufficient_evidence')
            .values('id', 'machine__model', 'question', 'timestamp')[:10]
        )

        return Response({
            "total_questions": total,
            "answered_count": answered,
            "insufficient_evidence_count": insufficient,
            "error_count": error,
            "per_machine": list(machine_stats),
            "recent_unanswered": list(unanswered_questions)
        })
