from django.db import models
from django.conf import settings
from machines.models import Machine

class QuestionHistory(models.Model):
    STATUS_CHOICES = (
        ('answered', 'Answered'),
        ('insufficient_evidence', 'Insufficient Evidence'),
        ('error', 'Error'),
    )

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='question_history')
    machine = models.ForeignKey(Machine, on_delete=models.CASCADE, related_name='history')
    question = models.TextField()
    answer = models.TextField()
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='answered')
    sources = models.JSONField(default=list, help_text="List of cited documents and pages")
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"[{self.machine.machine_id}] {self.question[:40]}... ({self.status})"
