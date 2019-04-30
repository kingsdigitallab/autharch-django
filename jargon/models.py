from django.db import models
from model_utils.models import TimeStampedModel


class BaseJargonModel(TimeStampedModel):
    title = models.CharField(max_length=128, unique=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


class EntityRelationType(BaseJargonModel):
    class Meta:
        verbose_name = 'EAC: Entity relation type'


class EntityType(BaseJargonModel):
    class Meta:
        verbose_name = 'EAC: Entity type'


class Function(BaseJargonModel):
    class Meta:
        verbose_name = 'EAC: Function'


class MaintenanceStatus(BaseJargonModel):
    class Meta:
        verbose_name = 'EAC: Name authority file status'
        verbose_name_plural = 'EAC: Name authority file status'


class NamePartType(BaseJargonModel):
    class Meta:
        verbose_name = 'EAC: Name part type'
        verbose_name_plural = 'EAC: Name part types'


class Publication(TimeStampedModel):
    title = models.TextField(unique=True)

    class Meta:
        verbose_name = 'EAD: Publication'

    def __str__(self):
        return self.title


class PublicationStatus(BaseJargonModel):
    is_archival = models.BooleanField(default=True)
    is_authority = models.BooleanField(default=True)

    class Meta:
        verbose_name_plural = 'EAC/EAD: Publication status'


class RecordType(BaseJargonModel):
    class Meta:
        verbose_name = 'EAD: Record type'
        verbose_name_plural = 'EAD: Record types'


class ReferenceSource(BaseJargonModel):
    class Meta:
        verbose_name = 'EAD: Reference source'


class Repository(BaseJargonModel):
    code = models.PositiveIntegerField()

    class Meta:
        unique_together = ['code', 'title']
        verbose_name = 'EAD: Repository'
        verbose_name_plural = 'EAD: Repositories'


class ResourceRelationType(BaseJargonModel):
    class Meta:
        verbose_name_plural = 'EAC: Resource relation types'
