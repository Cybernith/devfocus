from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import ApiRequestLog
from core.models import  GeneratedReport, Insight

User = get_user_model()


class ApiLoggingAndSseTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='log-user', password='pass')
        self.client.force_login(self.user)

    def test_api_request_logging_middleware_creates_log(self):
        url = reverse('task-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        self.assertGreaterEqual(ApiRequestLog.objects.count(), 1)
        log = ApiRequestLog.objects.first()
        self.assertTrue(log.path.startswith('/api/'))
        self.assertEqual(log.user, self.user)

    def test_event_stream_requires_auth_and_returns_sse(self):
        report = GeneratedReport.objects.create(
            user=self.user,
            type='DAILY',
            payload={'sessions': []},
        )
        Insight.objects.create(
            user=self.user,
            report=report,
            code='DEMO',
            level='INFO',
            message='demo insight',
        )

        self.client.logout()
        url = reverse('event-stream')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_401_UNAUTHORIZED)

        self.client.force_login(self.user)
        resp2 = self.client.get(url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertIn('text/event-stream', resp2['Content-Type'])
