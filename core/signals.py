from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from core.models import ContextSwitch, DevSession
from core.services import SessionService


@receiver(post_save, sender=ContextSwitch)
def update_session_on_context_switch(sender, instance: ContextSwitch, created, **kwargs):
    if not created:
        return
    session = instance.dev_session
    session.switch_count = session.context_switches.count()
    session.last_switch_at = instance.happened_at or timezone.now()
    session.save(update_fields=['switch_count', 'last_switch_at', 'updated_at'])


@receiver(post_save, sender=DevSession)
def auto_compute_focus_on_done(sender, instance: DevSession, created, **kwargs):
    if created:
        return
    if instance.status == DevSession.STATUS_DONE and instance.ended_at:
        SessionService.close_session(instance)
