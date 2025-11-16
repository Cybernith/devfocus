from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Task(TimeStampedModel):
    TYPE_BUG = 'BUG'
    TYPE_FEATURE = 'FEATURE'
    TYPE_REFACTOR = 'REFACTOR'

    TYPE_CHOICES = [
        (TYPE_BUG, 'Bug'),
        (TYPE_FEATURE, 'Feature'),
        (TYPE_REFACTOR, 'Refactor'),
    ]

    PRIORITY_LOW = 'LOW'
    PRIORITY_MEDIUM = 'MED'
    PRIORITY_HIGH = 'HIGH'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, 'Low'),
        (PRIORITY_MEDIUM, 'Medium'),
        (PRIORITY_HIGH, 'High'),
    ]

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    external_id = models.CharField(max_length=128, blank=True, null=True)
    type = models.CharField(max_length=16, choices=TYPE_CHOICES, default=TYPE_FEATURE)
    priority = models.CharField(max_length=8, choices=PRIORITY_CHOICES, default=PRIORITY_MEDIUM)

    def __str__(self) -> str:
        return self.title


class DevSession(TimeStampedModel):
    STATUS_OPEN = 'OPEN'
    STATUS_PAUSED = 'PAUSED'
    STATUS_DONE = 'DONE'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_PAUSED, 'Paused'),
        (STATUS_DONE, 'Done'),
    ]

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='dev_sessions')
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OPEN)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(blank=True, null=True)

    switch_count = models.PositiveIntegerField(default=0)
    last_switch_at = models.DateTimeField(blank=True, null=True)
    total_focus_minutes = models.PositiveIntegerField(default=0)

    tasks = models.ManyToManyField(Task, through='SessionTask', related_name='sessions')

    def __str__(self) -> str:
        return f"{self.title} ({self.get_status_display()})"

    @property
    def is_active(self) -> bool:
        return self.status in {self.STATUS_OPEN, self.STATUS_PAUSED}


class SessionTask(TimeStampedModel):
    ROLE_MAIN = 'MAIN'
    ROLE_SIDE = 'SIDE'

    ROLE_CHOICES = [
        (ROLE_MAIN, 'Main'),
        (ROLE_SIDE, 'Side'),
    ]

    dev_session = models.ForeignKey(DevSession, on_delete=models.CASCADE, related_name='session_tasks')
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='session_tasks')
    role = models.CharField(max_length=8, choices=ROLE_CHOICES, default=ROLE_MAIN)

    class Meta:
        unique_together = ('dev_session', 'task')

    def __str__(self):
        return f"{self.dev_session} → {self.task} ({self.role})"


class ContextSwitch(TimeStampedModel):
    REASON_INTERRUPT = 'INTERRUPT'
    REASON_QUICK_FIX = 'QUICK_FIX'
    REASON_MEETING = 'MEETING'
    REASON_OTHER = 'OTHER'

    REASON_CHOICES = [
        (REASON_INTERRUPT, 'Interrupt'),
        (REASON_QUICK_FIX, 'Quick fix'),
        (REASON_MEETING, 'Meeting'),
        (REASON_OTHER, 'Other'),
    ]

    dev_session = models.ForeignKey(DevSession, on_delete=models.CASCADE, related_name='context_switches')
    from_task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL, related_name='switches_from')
    to_task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL, related_name='switches_to')
    reason = models.CharField(max_length=16, choices=REASON_CHOICES, default=REASON_OTHER)
    happened_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"ContextSwitch #{self.pk} in {self.dev_session_id}"


class ResourceLink(TimeStampedModel):
    TYPE_PR = 'PR'
    TYPE_ISSUE = 'ISSUE'
    TYPE_DOC = 'DOC'
    TYPE_ARTICLE = 'ARTICLE'
    TYPE_TOOL = 'TOOL'
    TYPE_OTHER = 'OTHER'

    TYPE_CHOICES = [
        (TYPE_PR, 'Pull Request'),
        (TYPE_ISSUE, 'Issue / Ticket'),
        (TYPE_DOC, 'Documentation'),
        (TYPE_ARTICLE, 'Article'),
        (TYPE_TOOL, 'Tool'),
        (TYPE_OTHER, 'Other'),
    ]

    dev_session = models.ForeignKey(DevSession, null=True, blank=True,
                                    on_delete=models.CASCADE, related_name='resource_links')
    task = models.ForeignKey(Task, null=True, blank=True,
                             on_delete=models.CASCADE, related_name='resource_links')

    type = models.CharField(max_length=16, choices=TYPE_CHOICES, default=TYPE_OTHER)
    title = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self):
        return self.title


class GeneratedReport(TimeStampedModel):
    TYPE_DAILY = 'DAILY'
    TYPE_SESSION = 'SESSION'

    TYPE_CHOICES = [
        (TYPE_DAILY, 'Daily'),
        (TYPE_SESSION, 'Session'),
    ]

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='generated_reports')
    dev_session = models.ForeignKey(DevSession, null=True, blank=True,
                                    on_delete=models.CASCADE, related_name='generated_reports')
    type = models.CharField(max_length=16, choices=TYPE_CHOICES)
    payload = models.JSONField()  # summary, metrics, etc.

    def __str__(self):
        return f"{self.type} report #{self.pk} for {self.user}"
