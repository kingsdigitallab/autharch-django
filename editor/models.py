from django.contrib.auth.models import User
from django.db import models

from reversion.models import Revision

from jargon.models import CollaborativeWorkspaceEditorType, EditingEventType


class EditorProfile(models.Model):

    ADMIN = 'AD'
    MODERATOR = 'MO'
    EDITOR = 'ED'
    VISITOR = 'VI'
    ROLE_CHOICES = (
        (ADMIN, 'Admin'),
        (MODERATOR, 'Moderator'),
        (EDITOR, 'Editor'),
        (VISITOR, 'Visitor'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE,
                                related_name='editor_profile')
    role = models.CharField(max_length=2, choices=ROLE_CHOICES,
                            default=VISITOR)


class RevisionMetadata(models.Model):

    revision = models.OneToOneField(Revision, on_delete=models.CASCADE,
                                    related_name='revision_metadata')
    editing_event_type = models.ForeignKey(EditingEventType,
                                           on_delete=models.PROTECT)
    collaborative_workspace_editor_type = models.ForeignKey(
        CollaborativeWorkspaceEditorType, on_delete=models.PROTECT)
