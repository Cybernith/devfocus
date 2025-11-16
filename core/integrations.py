from typing import Iterable

import httpx
from django.conf import settings

from .models import Task, Team


class GitHubIntegrationError(Exception):
    pass


class GitHubImporter:

    @staticmethod
    async def import_issues_for_repo(owner: str, repo: str, team: Team=None) -> Iterable[Task]:
        token = getattr(settings, 'GITHUB_TOKEN', None)
        if not token:
            raise GitHubIntegrationError('GITHUB_TOKEN is not configured')

        url = f'https://api.github.com/repos/{owner}/{repo}/issues'
        headers = {
            'Authorization': f'Bearer {token}',
            'Accept': 'application/vnd.github+json',
        }

        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code != 200:
                raise GitHubIntegrationError(f'GitHub API error: {resp.status_code} {resp.text}')

            data = resp.json()

        tasks: list[Task] = []
        for issue in data:
            if 'pull_request' in issue:
                continue

            task, _ = Task.objects.get_or_create(
                external_id=str(issue['id']),
                external_source=Task.SOURCE_GITHUB,
                defaults={
                    'title': issue['title'][:255],
                    'description': issue.get('body') or '',
                    'external_url': issue.get('html_url'),
                    'team': team,
                },
            )
            tasks.append(task)

        return tasks
