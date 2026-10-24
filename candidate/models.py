from django.db import models
from lib.choice import choice_enum_options
from enum import Enum


class Status(Enum):
    SEND = 'send'
    RECEIVED = 'received'
    READ = 'read'
    FAILED = 'failed'
    NOT_SENT = 'not_sent'


class Candidate(models.Model):
    candidate_id = models.AutoField(primary_key=True, verbose_name='Candidate ID')
    full_name = models.CharField(max_length=255)
    phone_number = models.CharField(max_length=20)  # e.g. 919876543210 (country code, no +)
    last_message = models.DateTimeField(null=True, blank=True)
    whatsapp_message_id = models.CharField(max_length=255, null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=choice_enum_options(Status),
        default=Status.NOT_SENT.value,
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.full_name

    class Meta:
        ordering = ['-timestamp']



class CandidateMessage(models.Model):
    candidate = models.ForeignKey(Candidate, on_delete=models.CASCADE, related_name='messages')
    message_id = models.CharField(max_length=255)
    message = models.TextField()
    status = models.CharField(
        max_length=20,
        choices=choice_enum_options(Status),
        default=Status.NOT_SENT.value,
    )
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message to {self.candidate.full_name} - Status: {self.status}"

    class Meta:
        ordering = ['-timestamp']