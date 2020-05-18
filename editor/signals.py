"""Signals and signal processors.

* Update the search index only when a custom signal is sent.
* Create an EditorProfile whenever a User is created.

Haystack has a poor interaction with django-polymorphic models and
django-reversion, in that reverting a Revision that includes an object
that has an associated search index and is a subclass of a polymorphic
base model results in an error that I couldn't get a fix for. And
rather than not use the realtime index updating, I created a new
signal and processor subclass. The signal should be sent from a view
immediately after a save is made (this includes reversions and
'deletions').

Further, since inline forms are saved after the parent, index fields
that use data from sub-fields doesn't get indexed until the next time
the parent is saved. This is a serious issue with Entity objects, in
which almost everything is in related models.

"""

from django.contrib.auth.models import User
from django.db.models import signals
import django.dispatch

import haystack.signals

from .models import EditorProfile


view_post_save = django.dispatch.Signal(providing_args=['instance'])


class HaystackRealtimeSignalProcessor(haystack.signals.BaseSignalProcessor):

    """A Haystack signal processor that does not connect the post_save
    signal, leaving handling of index updates to the new
    view_post_save signal.

    """

    def setup(self):
        view_post_save.connect(self.handle_save)

    def teardown(self):
        view_post_save.disconnect(self.handle_save)


@django.dispatch.receiver(signals.post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        EditorProfile.objects.create(user=instance)
