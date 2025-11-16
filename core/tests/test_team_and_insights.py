
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.utils import timezone

from core.helper import TeamPermissionService
from core.models import Team, TeamMembership, GeneratedReport, Insight
from core.services import InsightService

User = get_user_model()


class TeamAndPermissionTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(username='owner', password='pass')
        self.member = User.objects.create_user(username='member', password='pass')
        self.other = User.objects.create_user(username='other', password='pass')

        self.team = Team.objects.create(name='Core Team', slug='core-team', owner=self.owner)
        TeamMembership.objects.create(team=self.team, user=self.member, role=TeamMembership.ROLE_MEMBER)

    def test_team_membership_unique(self):
        with self.assertRaises(Exception):
            TeamMembership.objects.create(team=self.team, user=self.member, role=TeamMembership.ROLE_MEMBER)

    def test_team_permission_service_owner(self):
        self.assertTrue(TeamPermissionService.user_in_team(self.owner, self.team))

    def test_team_permission_service_member(self):
        self.assertTrue(TeamPermissionService.user_in_team(self.member, self.team))

    def test_team_permission_service_other(self):
        self.assertFalse(TeamPermissionService.user_in_team(self.other, self.team))


class InsightServiceTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='insight-user', password='pass')

    def test_insight_generated_for_high_switches_and_low_focus(self):
        payload = {
            "date": str(timezone.now().date()),
            "sessions": [
                {"id": 1, "switch_count": 8, "total_focus_minutes": 30},
                {"id": 2, "switch_count": 5, "total_focus_minutes": 20},
            ],
        }
        report = GeneratedReport.objects.create(
            user=self.user,
            type=GeneratedReport.TYPE_DAILY,
            payload=payload,
        )

        insights = InsightService.generate_for_report(report)

        self.assertGreaterEqual(len(insights), 2)

        codes = {i.code for i in insights}
        self.assertIn('HIGH_CONTEXT_SWITCHING', codes)
        self.assertIn('LOW_FOCUS_TIME', codes)

        self.assertEqual(Insight.objects.filter(report=report).count(), len(insights))
