from django.http import HttpResponse
import csv

from core.models import TeamMembership, Team


def csv_response(filename: str, fieldnames, rows):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(fieldnames)
    for row in rows:
        writer.writerow([row.get(field, '') for field in fieldnames])
    return response


class TeamPermissionService:
    @staticmethod
    def user_in_team(user, team: Team) -> bool:
        if team is None:
            return False
        if team.owner_id == user.id:
            return True
        return TeamMembership.objects.filter(team=team, user=user).exists()
