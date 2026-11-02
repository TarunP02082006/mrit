from rest_framework import serializers
from machines.models import Machine, Manual, DocumentChunk

class MachineSerializer(serializers.ModelSerializer):
    manual_count = serializers.IntegerField(source='manuals.count', read_only=True)

    class Meta:
        model = Machine
        fields = ['id', 'machine_id', 'model', 'machine_name', 'manual_count', 'created_at']


class ManualSerializer(serializers.ModelSerializer):
    machine_model = serializers.CharField(source='machine.model', read_only=True)
    machine_code = serializers.CharField(source='machine.machine_id', read_only=True)

    class Meta:
        model = Manual
        fields = ['id', 'machine', 'machine_code', 'machine_model', 'document_id', 'revision', 'filename', 'page_count', 'is_indexed', 'uploaded_at']


class DocumentChunkSerializer(serializers.ModelSerializer):
    class Meta:
        model = DocumentChunk
        fields = ['id', 'machine_id', 'document_id', 'revision', 'page_number', 'section_title', 'chunk_text', 'chunk_index']

