from django.http import HttpResponse
import csv


def csv_response(filename: str, fieldnames, rows):
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    writer = csv.writer(response)
    writer.writerow(fieldnames)
    for row in rows:
        writer.writerow([row.get(field, '') for field in fieldnames])
    return response
