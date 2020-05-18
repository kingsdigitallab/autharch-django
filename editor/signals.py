"""Signals and signal processors.

Haystack has a poor interaction with django-polymorphic models and
django-reversion, in that reverting a Revision that includes an object
that has an associated search index and is a subclass of a polymorphic
base model results in an error that I couldn't get a fix for. And
rather than not use the realtime index updating, I created a new
signal and processor subclass. The signal should be sent from a view
immediately after a save is made (this includes reversions and
'deletions').

Create an EditorProfile whenever a User is created.

"""

from django.contrib.auth.models import User
from django.db.models import signals
import django.dispatch

import haystack.signals

from authority.models import Entity

from .models import EditorProfile


view_post_save = django.dispatch.Signal(providing_args=['instance'])


class HaystackRealtimeSignalProcessor(haystack.signals.BaseSignalProcessor):

    """A Haystack signal processor that connects the post_save signal only
    for Entities, leaving handling of the ArchivalRecord subclasses to the
    new view_post_save signal."""

    def setup(self):
        signals.post_save.connect(self.handle_save, sender=Entity)
        signals.post_delete.connect(self.handle_delete)
        view_post_save.connect(self.handle_save)

    def teardown(self):
        signals.post_save.disconnect(self.handle_save, sender=Entity)
        signals.post_delete.disconnect(self.handle_delete)
        view_post_save.disconnect(self.handle_save)


@django.dispatch.receiver(signals.post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        EditorProfile.objects.create(user=instance)
