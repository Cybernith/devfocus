from celery import shared_task
from django.utils import timezone

from core.services import ReportService, InsightService


@shared_task
def process_report_request(request_id: int):
    from api.models import ReportRequest

    try:
        req = ReportRequest.objects.select_related('user').get(pk=request_id)
    except ReportRequest.DoesNotExist:
        return

    if req.status not in (ReportRequest.STATUS_PENDING, ReportRequest.STATUS_RUNNING):
        return

    req.status = ReportRequest.STATUS_RUNNING
    req.save(update_fields=['status', 'updated_at'])

    try:
        day = req.day or timezone.now().date()
        report = ReportService.generate_daily_report(req.user, day=day)
        InsightService.generate_for_report(report)

        req.result_report = report
        req.status = ReportRequest.STATUS_DONE
        req.save(update_fields=['result_report', 'status', 'updated_at'])
    except Exception as exc:
        req.status = ReportRequest.STATUS_FAILED
        req.error_message = str(exc)
        req.save(update_fields=['status', 'error_message', 'updated_at'])
        raise
