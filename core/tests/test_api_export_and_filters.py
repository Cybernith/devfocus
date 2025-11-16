from datetime import timedelta

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APITestCase

from core.models import Task, DevSession

User = get_user_model()


class DevSessionApiFilterOrderingExportTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser', password='pass')
        self.client.force_login(self.user)

        now = timezone.now()

        self.s1 = DevSession.objects.create(
            user=self.user,
            title='Old Session',
            status=DevSession.STATUS_DONE,
            created_at=now - timedelta(days=2),
            started_at=now - timedelta(days=2),
        )
        self.s2 = DevSession.objects.create(
            user=self.user,
            title='New Session',
            status=DevSession.STATUS_OPEN,
            created_at=now,
            started_at=now,
            switch_count=5,
        )

    def test_filter_by_status(self):
        url = reverse('session-list')
        resp = self.client.get(url, {'status': 'OPEN'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        ids = [item['id'] for item in resp.data]
        self.assertIn(self.s2.id, ids)
        self.assertNotIn(self.s1.id, ids)

    def test_ordering_by_switch_count_desc(self):
        url = reverse('session-list')
        resp = self.client.get(url, {'ordering': '-switch_count'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        ids = [item['id'] for item in resp.data]
        self.assertEqual(ids[0], self.s2.id)

    def test_export_sessions_csv(self):
        url = reverse('session-export')
        resp = self.client.get(url, {'format': 'csv'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('text/csv', resp['Content-Type'])
        self.assertIn('id,title,status', resp.content.decode('utf-8').splitlines()[0])

    def test_export_sessions_json(self):
        url = reverse('session-export')
        resp = self.client.get(url, {'format': 'json'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
        self.assertGreaterEqual(len(resp.data), 2)


class TaskApiFilterOrderingExportTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='apiuser2', password='pass')
        self.client.force_login(self.user)

        self.t1 = Task.objects.create(
            title='Fix bug',
            description='',
            type=Task.TYPE_BUG,
            priority=Task.PRIORITY_HIGH,
        )
        self.t2 = Task.objects.create(
            title='Write docs',
            description='',
            type=Task.TYPE_FEATURE,
            priority=Task.PRIORITY_LOW,
        )

    def test_filter_by_type_and_priority(self):
        url = reverse('task-list')
        resp = self.client.get(url, {'type': Task.TYPE_BUG, 'priority': Task.PRIORITY_HIGH})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        ids = [item['id'] for item in resp.data]
        self.assertIn(self.t1.id, ids)
        self.assertNotIn(self.t2.id, ids)

    def test_search_and_ordering(self):
        url = reverse('task-list')
        resp = self.client.get(url, {'search': 'docs', 'ordering': 'title'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        ids = [item['id'] for item in resp.data]
        self.assertIn(self.t2.id, ids)
        self.assertNotIn(self.t1.id, ids)

    def test_export_tasks_csv(self):
        url = reverse('task-export')
        resp = self.client.get(url, {'format': 'csv'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIn('text/csv', resp['Content-Type'])
        first_line = resp.content.decode('utf-8').splitlines()[0]
        self.assertIn('id,title,type,priority', first_line)

    def test_export_tasks_json(self):
        url = reverse('task-export')
        resp = self.client.get(url, {'format': 'json'})
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertIsInstance(resp.data, list)
        self.assertGreaterEqual(len(resp.data), 2)
