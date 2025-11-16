from typing import Optional

from django.utils.deprecation import MiddlewareMixin

from core.models import DevSession


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
