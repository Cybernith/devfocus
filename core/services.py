from dataclasses import dataclass
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from core.models import DevSession, GeneratedReport


@dataclass
class SessionSummary:
    session_id: int
    duration_minutes: int
    switch_count: int


class SessionService:
    @staticmethod
    def close_session(session: DevSession) -> DevSession:
        if session.ended_at is None:
            session.ended_at = timezone.now()

        duration = session.ended_at - session.started_at
        session.total_focus_minutes = max(int(duration.total_seconds() // 60), 0)
        session.status = DevSession.STATUS_DONE
        session.save(update_fields=['ended_at', 'total_focus_minutes', 'status', 'updated_at'])
        return session

    @staticmethod
    def compute_summary(session: DevSession) -> SessionSummary:
        duration = (session.ended_at or timezone.now()) - session.started_at
        switch_count = session.context_switches.count()
        return SessionSummary(
            session_id=session.pk,
            duration_minutes=max(int(duration.total_seconds() // 60), 0),
            switch_count=switch_count,
        )


class ReportService:
    @staticmethod
    def generate_daily_report(user, day=None) -> GeneratedReport:
        if day is None:
            day = timezone.now().date()

        start = timezone.make_aware(timezone.datetime.combine(day, timezone.datetime.min.time()))
        end = start + timedelta(days=1)

        sessions = (
            DevSession.objects
            .filter(user=user, created_at__gte=start, created_at__lt=end)
            .annotate(switch_count=Count('context_switches'))
        )

        payload = {
            "date": str(day),
            "sessions": [
                {
                    "id": s.id,
                    "title": s.title,
                    "status": s.status,
                    "switch_count": s.switch_count,
                    "total_focus_minutes": s.total_focus_minutes,
                }
                for s in sessions
            ],
        }

        report = GeneratedReport.objects.create(
            user=user,
            type=GeneratedReport.TYPE_DAILY,
            payload=payload,
        )
        return report
