from django.contrib.auth import get_user_model
from django.test import TestCase

from core.models import DevSession, ContextSwitch, Task, SessionTask

User = get_user_model()


class DevSessionContextSwitchSignalTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='u1', password='pass')
        self.session = DevSession.objects.create(
            user=self.user,
            title='Test Session',
            description='',
        )

    def test_context_switch_updates_session_counters(self):
        self.assertEqual(self.session.switch_count, 0)
        self.assertIsNone(self.session.last_switch_at)

        ContextSwitch.objects.create(
            dev_session=self.session,
            reason=ContextSwitch.REASON_OTHER,
        )

        self.session.refresh_from_db()
        self.assertEqual(self.session.switch_count, 1)
        self.assertIsNotNone(self.session.last_switch_at)

    def test_session_task_unique_together(self):
        task = Task.objects.create(title='T1', description='')
        SessionTask.objects.create(dev_session=self.session, task=task)

        with self.assertRaises(Exception):
            SessionTask.objects.create(dev_session=self.session, task=task)
