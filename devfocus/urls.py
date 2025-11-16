from django.contrib import admin
from django.urls import re_path, include, path
from django.http import JsonResponse
from typing import Any

from devfocus.home_page_view import home


def health_check(_: Any) -> JsonResponse:
    return JsonResponse({"status": "ok"})


urlpatterns = [
    path('', home),
    re_path(r"^admin/?", admin.site.urls),
    re_path(r"^health/?$", health_check, name="health"),
    re_path(r"^api/v1/", include(("api.urls", "api"), namespace="api-v1")),
]
