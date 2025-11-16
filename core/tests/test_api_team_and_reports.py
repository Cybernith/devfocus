from unittest import mock

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from api.models import ReportRequest
from core.models import Team, TeamMembership, GeneratedReport, Insight

User = get_user_model()


class TeamApiTests(APITestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.member = User.objects.create_user(username='member', password='pass')
        self.client.force_login(self.owner)

    def test_create_team_and_list_members(self):
        url = reverse('team-list')
        resp = self.client.post(url, {'name': 'Backend Team', 'slug': 'backend-team'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        team_id = resp.data['id']
        team = Team.objects.get(pk=team_id)
        TeamMembership.objects.create(team=team, user=self.member, role=TeamMembership.ROLE_MEMBER)

        members_url = reverse('team-members', args=[team_id])
        resp2 = self.client.get(members_url)
        self.assertEqual(resp2.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp2.data), 1)


class ReportRequestApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='report-api', password='pass')
        self.client.force_login(self.user)

    @mock.patch('core.tasks.process_report_request.delay')
    def test_create_report_request_triggers_task(self, mock_delay):
        url = reverse('report-request-list')
        resp = self.client.post(url, {'type': 'DAILY'})
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        req_id = resp.data['id']
        self.assertTrue(ReportRequest.objects.filter(pk=req_id).exists())
        mock_delay.assert_called_once_with(req_id)


class InsightApiTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='insight-api', password='pass')
        self.client.force_login(self.user)

        report = GeneratedReport.objects.create(
            user=self.user,
            type='DAILY',
            payload={"sessions": []},
        )
        Insight.objects.create(
            user=self.user,
            report=report,
            code='TEST_CODE',
            level='INFO',
            message='Test',
        )

    def test_list_insights(self):
        url = reverse('insight-list')
        resp = self.client.get(url)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(resp.data), 1)
        self.assertEqual(resp.data[0]['code'], 'TEST_CODE')
