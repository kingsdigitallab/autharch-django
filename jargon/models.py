from django.db import models
from model_utils.models import TimeStampedModel


class BaseJargonModel(TimeStampedModel):
    title = models.CharField(max_length=128, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class EntityRelationType(BaseJargonModel):
    pass


class EntityType(BaseJargonModel):
    pass


class FamilyTreeLevel(BaseJargonModel):
    pass


class Function(BaseJargonModel):
    pass


class MaintenanceStatus(BaseJargonModel):
    class Meta:
        verbose_name = 'Name authority file status'
        verbose_name_plural = 'Name authority file statuses'


class NamePartType(BaseJargonModel):
    pass


class Publication(TimeStampedModel):
    title = models.TextField(unique=True)

    def __str__(self):
        return self.title


class PublicationStatus(BaseJargonModel):
    class Meta:
        verbose_name_plural = 'Publication status'


class RecordType(BaseJargonModel):
    pass


class ResourceType(BaseJargonModel):
    pass
