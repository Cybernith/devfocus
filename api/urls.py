from django.urls import include, re_path
from rest_framework.routers import DefaultRouter

from api.views import (
    TaskViewSet,
    DevSessionViewSet,
    ContextSwitchViewSet,
    ResourceLinkViewSet,
    GeneratedReportViewSet,
    DailyReportView,
    AsyncDailyReportView,
)

router = DefaultRouter()
router.register(r"tasks", TaskViewSet, basename="task")
router.register(r"sessions", DevSessionViewSet, basename="session")
router.register(r"context-switches", ContextSwitchViewSet, basename="context-switch")
router.register(r"resources", ResourceLinkViewSet, basename="resource")
router.register(r"reports", GeneratedReportViewSet, basename="generated-report")


urlpatterns = [
    re_path(r"^", include(router.urls)),
    re_path(r"^reports/daily/?$", DailyReportView.as_view(), name="daily-report"),
    re_path(r"^reports/daily-async/?$", AsyncDailyReportView.as_view(), name="daily-report-async"),
]
