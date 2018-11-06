from django.db import models
from reversion.models import Revision


class RevisionEvent(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class EditorType(models.Model):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class RevisionMetadata(models.Model):
    revision = models.OneToOneField(Revision, on_delete=models.CASCADE)
    event_type = models.ForeignKey(RevisionEvent, on_delete=models.PROTECT)
    editor_type = models.ForeignKey(EditorType, on_delete=models.PROTECT)
