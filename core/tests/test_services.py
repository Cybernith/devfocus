from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.models import DevSession, GeneratedReport
from core.services import SessionService, ReportService

User = get_user_model()


class SessionServiceTests(TestCase):
    def setUp(self):
        self.user = User.create_user = User.objects.create_user(
            username='u2', password='pass'
        )
        now = timezone.now()
        self.session = DevSession.objects.create(
            user=self.user,
            title='Focus Session',
            started_at=now - timedelta(minutes=90),
            status=DevSession.STATUS_OPEN,
        )

    def test_close_session_sets_total_focus_minutes_and_status(self):
        SessionService.close_session(self.session)
        self.session.refresh_from_db()

        self.assertEqual(self.session.status, DevSession.STATUS_DONE)
        self.assertIsNotNone(self.session.ended_at)
        self.assertGreater(self.session.total_focus_minutes, 0)


class ReportServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u3', password='pass')
        self.today = timezone.now().date()
        yesterday = self.today - timedelta(days=1)

        DevSession.objects.create(
            user=self.user,
            title='Today Session 1',
            started_at=timezone.now(),
            status=DevSession.STATUS_DONE,
        )
        DevSession.objects.create(
            user=self.user,
            title='Yesterday Session',
            started_at=timezone.make_aware(
                timezone.datetime.combine(yesterday, timezone.datetime.min.time())
            ),
            status=DevSession.STATUS_DONE,
        )

    def test_generate_daily_report_only_includes_today_sessions(self):
        report = ReportService.generate_daily_report(self.user, day=self.today)

        self.assertIsInstance(report, GeneratedReport)
        payload = report.payload
        self.assertEqual(payload['date'], str(self.today))

        titles = {s['title'] for s in payload['sessions']}
        self.assertIn('Today Session 1', titles)
        self.assertNotIn('Yesterday Session', titles)
