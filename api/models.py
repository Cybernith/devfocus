from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models

from core.models import TimeStampedModel, GeneratedReport


class ReportRequest(TimeStampedModel):
    TYPE_DAILY = 'DAILY'
    TYPE_WEEKLY = 'WEEKLY'

    TYPE_CHOICES = [
        (TYPE_DAILY, 'Daily'),
        (TYPE_WEEKLY, 'Weekly'),
    ]

    STATUS_PENDING = 'PENDING'
    STATUS_RUNNING = 'RUNNING'
    STATUS_DONE = 'DONE'
    STATUS_FAILED = 'FAILED'

    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending'),
        (STATUS_RUNNING, 'Running'),
        (STATUS_DONE, 'Done'),
        (STATUS_FAILED, 'Failed'),
    ]

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='report_requests')
    type = models.CharField(max_length=16, choices=TYPE_CHOICES, default=TYPE_DAILY)
    day = models.DateField(blank=True, null=True)

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_PENDING)
    error_message = models.TextField(blank=True, null=True)

    result_report = models.ForeignKey(
        GeneratedReport,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='requests',
    )

    def __str__(self):
        return f"ReportRequest #{self.pk} ({self.type}, {self.status})"


class ApiRequestLog(TimeStampedModel):
    user = models.ForeignKey(
        AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='api_logs',
    )
    path = models.CharField(max_length=512)
    method = models.CharField(max_length=8)
    status_code = models.PositiveIntegerField()
    duration_ms = models.FloatField()
    user_agent = models.CharField(max_length=512, blank=True)
    remote_addr = models.GenericIPAddressField(null=True, blank=True)

    def __str__(self):
        return f"{self.method} {self.path} [{self.status_code}]"