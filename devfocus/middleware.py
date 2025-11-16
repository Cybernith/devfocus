from api.models import ApiRequestLog

from typing import Optional
import time

from django.utils.deprecation import MiddlewareMixin
from django.http import HttpRequest, HttpResponse

from core.models import DevSession


class ApiRequestLoggingMiddleware(MiddlewareMixin):

    def process_request(self, request: HttpRequest):
        request._start_time = time.perf_counter()

    def process_response(self, request: HttpRequest, response: HttpResponse):
        start = getattr(request, '_start_time', None)
        duration_ms = None
        if start is not None:
            duration_ms = (time.perf_counter() - start) * 1000.0

        if request.path.startswith('/api/'):
            user = getattr(request, 'user', None)
            ApiRequestLog.objects.create(
                user=user if getattr(user, 'is_authenticated', False) else None,
                path=request.path,
                method=request.method,
                status_code=response.status_code,
                duration_ms=duration_ms or 0.0,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:512],
                remote_addr=request.META.get('REMOTE_ADDR'),
            )

        return response


class DevSessionMiddleware(MiddlewareMixin):

    def process_request(self, request):

        request.dev_session: Optional[DevSession] = None

        session_id = (
            request.headers.get('X-Dev-Session-Id')
            or request.GET.get('dev_session_id')
        )

        if not session_id:
            return

        try:
            session = DevSession.objects.select_related('user').get(
                pk=session_id,
                status__in=[DevSession.STATUS_OPEN, DevSession.STATUS_PAUSED],
            )
        except (DevSession.DoesNotExist, ValueError):
            return

        request.dev_session = session


