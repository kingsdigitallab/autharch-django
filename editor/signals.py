"""Signals and signal processor.

Haystack has a poor interaction with django-polymorphic models and
django-reversion, in that reverting a Revision that includes an object
that has an associated search index and is a subclass of a polymorphic
base model results in an error that I couldn't get a fix for. And
rather than not use the realtime index updating, I created a new
signal and processor subclass. The signal should be sent from a view
immediately after a save is made (this includes reversions and
'deletions').

"""

from django.db import models
import django.dispatch

import haystack.signals

from authority.models import Entity


view_post_save = django.dispatch.Signal(providing_args=['instance'])


class HaystackRealtimeSignalProcessor(haystack.signals.BaseSignalProcessor):

    """A Haystack signal processor that connects the post_save signal only
    for Entities, leaving handling of the ArchivalRecord subclasses to the
    new view_post_save signal."""

    def setup(self):
        models.signals.post_save.connect(self.handle_save, sender=Entity)
        models.signals.post_delete.connect(self.handle_delete)
        view_post_save.connect(self.handle_save)

    def teardown(self):
        models.signals.post_save.disconnect(self.handle_save, sender=Entity)
        models.signals.post_delete.disconnect(self.handle_delete)
        view_post_save.disconnect(self.handle_save)
