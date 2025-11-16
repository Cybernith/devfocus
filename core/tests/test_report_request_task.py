from datetime import timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from api.models import ReportRequest
from core.models import DevSession, GeneratedReport, Insight
from core.tasks import process_report_request

User = get_user_model()


class ReportRequestTaskTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='report-user', password='pass')
        now = timezone.now()

        DevSession.objects.create(
            user=self.user,
            title='Today Focus',
            started_at=now - timedelta(minutes=60),
            status='DONE',
            total_focus_minutes=60,
        )

        self.req = ReportRequest.objects.create(
            user=self.user,
            type=ReportRequest.TYPE_DAILY,
            day=now.date(),
        )

    def test_process_report_request_creates_report_and_insights(self):
        process_report_request(self.req.id)

        self.req.refresh_from_db()
        self.assertEqual(self.req.status, ReportRequest.STATUS_DONE)
        self.assertIsNotNone(self.req.result_report)

        report = self.req.result_report
        self.assertIsInstance(report, GeneratedReport)

        self.assertGreaterEqual(Insight.objects.filter(report=report).count(), 0)

    def test_process_report_request_handles_missing_request(self):
        process_report_request(9999)
