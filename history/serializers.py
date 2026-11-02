from rest_framework import serializers
from history.models import QuestionHistory

class QuestionHistorySerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    user_role = serializers.CharField(source='user.role', read_only=True)
    machine_model = serializers.CharField(source='machine.model', read_only=True)
    machine_code = serializers.CharField(source='machine.machine_id', read_only=True)

    class Meta:
        model = QuestionHistory
        fields = [
            'id', 'user', 'username', 'user_role', 'machine', 'machine_code', 'machine_model',
            'question', 'answer', 'status', 'sources', 'timestamp'
        ]

