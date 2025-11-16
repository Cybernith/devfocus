from datetime import date

import httpx
from asgiref.sync import sync_to_async
from django.utils import timezone
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.views import APIView

from core.helper import csv_response
from core.models import Task, DevSession, SessionTask, ContextSwitch, ResourceLink, GeneratedReport
from core.services import SessionService, ReportService
from api.serializers import (
    TaskSerializer,
    DevSessionSerializer,
    DevSessionDetailSerializer,
    CreateDevSessionSerializer,
    SessionTaskSerializer,
    ContextSwitchSerializer,
    ResourceLinkSerializer,
    GeneratedReportSerializer,
)


class IsOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        user = getattr(obj, 'user', None) or getattr(getattr(obj, 'dev_session', None), 'user', None)
        if user is None:
            return False
        return user == request.user


class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        qs = Task.objects.all().order_by('-created_at')

        type_ = self.request.query_params.get('type')
        priority = self.request.query_params.get('priority')
        search = self.request.query_params.get('search')

        if type_:
            qs = qs.filter(type=type_)
        if priority:
            qs = qs.filter(priority=priority)
        if search:
            qs = qs.filter(title__icontains=search)

        ordering = self.request.query_params.get('ordering')
        allowed = {'created_at', 'updated_at', 'priority', 'title'}
        if ordering:
            field = ordering.lstrip('-')
            if field in allowed:
                qs = qs.order_by(ordering)

        return qs

    @action(detail=False, methods=['get'])
    def export(self, request):
        fmt = request.query_params.get('format', 'csv').lower()
        qs = self.get_queryset()
        serializer = self.get_serializer(qs, many=True)

        if fmt == 'json':
            return Response(serializer.data)

        fieldnames = ['id', 'title', 'type', 'priority', 'external_id', 'created_at', 'updated_at']
        return csv_response('tasks.csv', fieldnames, serializer.data)


class DevSessionViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        qs = DevSession.objects.filter(user=self.request.user)

        status_param = self.request.query_params.get('status')
        date_from = self.request.query_params.get('date_from')
        date_to = self.request.query_params.get('date_to')
        title_search = self.request.query_params.get('search')

        if status_param:
            qs = qs.filter(status=status_param)

        if date_from:
            qs = qs.filter(created_at__date__gte=date_from)

        if date_to:
            qs = qs.filter(created_at__date__lte=date_to)

        if title_search:
            qs = qs.filter(title__icontains=title_search)

        ordering = self.request.query_params.get('ordering')
        allowed = {
            'created_at',
            'updated_at',
            'started_at',
            'ended_at',
            'switch_count',
            'total_focus_minutes',
        }
        if ordering:
            field = ordering.lstrip('-')
            if field in allowed:
                qs = qs.order_by(ordering)
        else:
            qs = qs.order_by('-created_at')

        return qs

    def get_serializer_class(self):
        if self.action == 'retrieve':
            return DevSessionDetailSerializer
        if self.action == 'create':
            return CreateDevSessionSerializer
        return DevSessionSerializer

    def perform_create(self, serializer):
        serializer.save()

    @action(detail=True, methods=['post'])
    def close(self, request, pk=None):
        session = self.get_object()
        SessionService.close_session(session)
        return Response(DevSessionSerializer(session).data)

    @action(detail=True, methods=['post'])
    def attach_task(self, request, pk=None):
        session = self.get_object()
        task_id = request.data.get('task_id')
        role = request.data.get('role', SessionTask.ROLE_MAIN)
        if not task_id:
            return Response({"detail": "task_id is required"}, status=status.HTTP_400_BAD_REQUEST)

        task = Task.objects.get(pk=task_id)
        st, created = SessionTask.objects.get_or_create(
            dev_session=session,
            task=task,
            defaults={'role': role},
        )
        if not created:
            st.role = role
            st.save(update_fields=['role', 'updated_at'])

        return Response(SessionTaskSerializer(st).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def export(self, request):
        fmt = request.query_params.get('format', 'csv').lower()
        qs = self.get_queryset()
        serializer = DevSessionSerializer(qs, many=True)

        if fmt == 'json':
            return Response(serializer.data)

        fieldnames = [
            'id', 'title', 'status',
            'started_at', 'ended_at',
            'switch_count', 'total_focus_minutes',
            'created_at', 'updated_at',
        ]
        return csv_response('sessions.csv', fieldnames, serializer.data)


class ContextSwitchViewSet(viewsets.ModelViewSet):
    serializer_class = ContextSwitchSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return ContextSwitch.objects.filter(dev_session__user=self.request.user).order_by('-happened_at')


class ResourceLinkViewSet(viewsets.ModelViewSet):
    serializer_class = ResourceLinkSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwner]

    def get_queryset(self):
        return ResourceLink.objects.filter(
            dev_session__user=self.request.user
        ).order_by('-created_at')


class GeneratedReportViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = GeneratedReportSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return GeneratedReport.objects.filter(user=self.request.user).order_by('-created_at')


class DailyReportView(APIView):
    """
    Sync view – uses domain service ReportService to compute daily report.
    """

    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        day_str = request.data.get('date')
        if day_str:
            day = date.fromisoformat(day_str)
        else:
            day = timezone.now().date()

        report = ReportService.generate_daily_report(request.user, day=day)
        return Response(GeneratedReportSerializer(report).data, status=status.HTTP_201_CREATED)


class AsyncDailyReportView(APIView):

    permission_classes = [permissions.IsAuthenticated]

    async def post(self, request):
        payload = {
            "user_id": request.user.id,
            "now": timezone.now().isoformat(),
        }

        async with httpx.AsyncClient(timeout=5.0) as client:
            try:
                resp = await client.post("https://httpbin.org/post", json=payload)
                external_data = resp.json()
            except Exception:
                external_data = {"error": "external service unavailable"}

        report = await sync_to_async(ReportService.generate_daily_report)(request.user)

        data = GeneratedReportSerializer(report).data
        data["external"] = external_data

        return Response(data, status=status.HTTP_201_CREATED)
