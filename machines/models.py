import os
from django.db import models

class Machine(models.Model):
    machine_id = models.CharField(max_length=50, unique=True, help_text="e.g. M-HP200, M-AC90")
    model = models.CharField(max_length=50, help_text="e.g. HP-200, AC-90")
    machine_name = models.CharField(max_length=150, help_text="e.g. Hydraulic forming press")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.machine_id} - {self.model} ({self.machine_name})"

    class Meta:
        ordering = ['machine_id']


class Manual(models.Model):
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='manuals')
    document_id = models.CharField(max_length=50, help_text="e.g. HP-OPS-01, HP-MNT-01, AC-OM-01")
    revision = models.CharField(max_length=20, default='1.0')
    pdf_file = models.FileField(upload_to='manuals_pdf/')
    filename = models.CharField(max_length=255)
    page_count = models.IntegerField(default=3)
    is_indexed = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.document_id} Rev {self.revision} ({self.machine.model}) - {self.filename}"

    class Meta:
        unique_together = ('machine', 'document_id', 'revision')
        ordering = ['document_id']


class DocumentChunk(models.Model):
    manual = models.ForeignKey(Manual, on_delete=models.CASCADE, related_name='chunks')
    machine_id = models.CharField(max_length=50, db_index=True)
    document_id = models.CharField(max_length=50, db_index=True)
    revision = models.CharField(max_length=20)
    page_number = models.IntegerField(help_text="1-based original PDF page number")
    section_title = models.CharField(max_length=255, blank=True, default='')
    chunk_text = models.TextField()
    chunk_index = models.IntegerField(default=0)

    def __str__(self):
        return f"[{self.machine_id}] {self.document_id} p.{self.page_number} (#{self.chunk_index})"

    class Meta:
        indexes = [
            models.Index(fields=['machine_id']),
            models.Index(fields=['document_id', 'page_number']),
        ]
        ordering = ['machine_id', 'document_id', 'page_number', 'chunk_index']
