from django.conf.global_settings import AUTH_USER_MODEL
from django.db import models
from django.utils import timezone


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Team(TimeStampedModel):
    name = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    owner = models.ForeignKey(
        AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='owned_teams',
    )

    members = models.ManyToManyField(
        AUTH_USER_MODEL,
        through='TeamMembership',
        related_name='teams',
    )

    def __str__(self):
        return self.name


class TeamMembership(TimeStampedModel):
    ROLE_OWNER = 'OWNER'
    ROLE_ADMIN = 'ADMIN'
    ROLE_MEMBER = 'MEMBER'
    ROLE_VIEWER = 'VIEWER'

    ROLE_CHOICES = [
        (ROLE_OWNER, 'Owner'),
        (ROLE_ADMIN, 'Admin'),
        (ROLE_MEMBER, 'Member'),
        (ROLE_VIEWER, 'Viewer'),
    ]

    team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='memberships')
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default=ROLE_MEMBER)

    class Meta:
        unique_together = ('team', 'user')

    def __str__(self):
        return f"{self.user} @ {self.team} ({self.role})"


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

    SOURCE_GITHUB = 'GITHUB'
    SOURCE_JIRA = 'JIRA'
    SOURCE_MANUAL = 'MANUAL'

    SOURCE_CHOICES = [
        (SOURCE_GITHUB, 'GitHub'),
        (SOURCE_JIRA, 'Jira'),
        (SOURCE_MANUAL, 'Manual'),
    ]

    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='tasks')

    external_id = models.CharField(max_length=128, blank=True, null=True)
    external_source = models.CharField(max_length=16, choices=SOURCE_CHOICES, default=SOURCE_MANUAL)
    external_url = models.URLField(blank=True, null=True)

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
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
    tasks = models.ManyToManyField(Task, through='SessionTask', related_name='sessions')
    team = models.ForeignKey(Team, null=True, blank=True, on_delete=models.SET_NULL, related_name='dev_sessions')

    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    status = models.CharField(max_length=16, choices=STATUS_CHOICES, default=STATUS_OPEN)
    started_at = models.DateTimeField(default=timezone.now)
    ended_at = models.DateTimeField(blank=True, null=True)

    switch_count = models.PositiveIntegerField(default=0)
    last_switch_at = models.DateTimeField(blank=True, null=True)
    total_focus_minutes = models.PositiveIntegerField(default=0)

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
    payload = models.JSONField()

    def __str__(self):
        return f"{self.type} report #{self.pk} for {self.user}"


class Insight(TimeStampedModel):
    LEVEL_INFO = 'INFO'
    LEVEL_WARN = 'WARN'

    LEVEL_CHOICES = [
        (LEVEL_INFO, 'Info'),
        (LEVEL_WARN, 'Warning'),
    ]

    user = models.ForeignKey(AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='insights')
    dev_session = models.ForeignKey(DevSession, null=True, blank=True, on_delete=models.CASCADE, related_name='insights')
    report = models.ForeignKey(GeneratedReport, null=True, blank=True, on_delete=models.CASCADE, related_name='insights')

    code = models.CharField(max_length=64)
    level = models.CharField(max_length=16, choices=LEVEL_CHOICES, default=LEVEL_INFO)
    message = models.TextField()
    meta = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.code} ({self.level})"

