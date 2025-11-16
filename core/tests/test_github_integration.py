import asyncio
from unittest import mock

from django.conf import settings
from django.test import TestCase

from core.integrations import GitHubImporter, GitHubIntegrationError
from core.models import Task, Team


class GitHubImporterTests(TestCase):
    def setUp(self):
        settings.GITHUB_TOKEN = 'dummy-token'
        self.team = Team.objects.create(name='GH Team', slug='gh-team', owner_id=None)

    def _run_async(self, coro):
        return asyncio.get_event_loop().run_until_complete(coro)

    @mock.patch('core.integrations.httpx.AsyncClient')
    def test_import_issues_creates_tasks(self, mock_client_cls):
        mock_client = mock.MagicMock()
        mock_client_cls.return_value.__aenter__.return_value = mock_client

        mock_client.get.return_value.status_code = 200
        mock_client.get.return_value.json.return_value = [
            {
                'id': 123,
                'title': 'Sample issue',
                'body': 'Issue body',
                'html_url': 'https://github.com/owner/repo/issues/1',
            },
            {
                'id': 456,
                'title': 'Another issue',
                'body': '',
                'html_url': 'https://github.com/owner/repo/issues/2',
                'pull_request': {},
            },
        ]

        tasks = self._run_async(
            GitHubImporter.import_issues_for_repo('owner', 'repo', team=self.team)
        )

        self.assertEqual(len(tasks), 1)
        t = tasks[0]
        self.assertEqual(t.external_id, '123')
        self.assertEqual(t.external_source, Task.SOURCE_GITHUB)
        self.assertEqual(Task.objects.count(), 1)

    def test_import_issues_without_token_raises(self):
        settings.GITHUB_TOKEN = ''
        with self.assertRaises(GitHubIntegrationError):
            self._run_async(GitHubImporter.import_issues_for_repo('o', 'r', team=None))
