from django.contrib.auth import get_user_model
from rest_framework import serializers

from core.models import Task, DevSession, SessionTask, ContextSwitch, ResourceLink, GeneratedReport

User = get_user_model()


class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ['id', 'title', 'description', 'external_id', 'type', 'priority', 'created_at', 'updated_at']


class DevSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DevSession
        fields = [
            'id', 'title', 'description', 'status',
            'started_at', 'ended_at',
            'switch_count', 'last_switch_at', 'total_focus_minutes',
            'created_at', 'updated_at',
        ]
        read_only_fields = ['switch_count', 'last_switch_at', 'total_focus_minutes']


class DevSessionDetailSerializer(DevSessionSerializer):
    tasks = TaskSerializer(source='tasks', many=True, read_only=True)

    class Meta(DevSessionSerializer.Meta):
        fields = DevSessionSerializer.Meta.fields + ['tasks']


class CreateDevSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = DevSession
        fields = ['id', 'title', 'description']

    def create(self, validated_data):
        user = self.context['request'].user
        return DevSession.objects.create(user=user, **validated_data)


class SessionTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionTask
        fields = ['id', 'dev_session', 'task', 'role', 'created_at', 'updated_at']


class ContextSwitchSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContextSwitch
        fields = [
            'id', 'dev_session', 'from_task', 'to_task',
            'reason', 'happened_at', 'created_at', 'updated_at',
        ]


class ResourceLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = ResourceLink
        fields = [
            'id', 'dev_session', 'task', 'type',
            'title', 'url', 'created_at', 'updated_at',
        ]


class GeneratedReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = GeneratedReport
        fields = ['id', 'type', 'payload', 'created_at']
