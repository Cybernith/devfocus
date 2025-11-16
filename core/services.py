from dataclasses import dataclass
from datetime import timedelta

from django.db.models import Count
from django.utils import timezone

from core.models import DevSession, GeneratedReport, Insight


class InsightService:
    @staticmethod
    def generate_for_report(report: GeneratedReport) -> list[Insight]:
        user = report.user
        payload = report.payload
        sessions = payload.get('sessions', [])

        insights: list[Insight] = []

        total_switches = sum(s.get('switch_count', 0) for s in sessions)
        total_focus = sum(s.get('total_focus_minutes', 0) for s in sessions)

        if total_switches > 10:
            insights.append(Insight.objects.create(
                user=user,
                report=report,
                code='HIGH_CONTEXT_SWITCHING',
                level=Insight.LEVEL_WARN,
                message='High context switching detected; consider reducing parallel tasks.',
                meta={'total_switches': total_switches},
            ))

        if total_focus < 60:
            insights.append(Insight.objects.create(
                user=user,
                report=report,
                code='LOW_FOCUS_TIME',
                level=Insight.LEVEL_INFO,
                message='Low focused coding time today; maybe schedule a longer deep-work block.',
                meta={'total_focus_minutes': total_focus},
            ))

        return insights


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
        InsightService.generate_for_report(report)
        return report
