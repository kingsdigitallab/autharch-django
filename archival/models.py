import reversion
from authority.models import Entity
from django.conf import settings
from django.db import models
from geonames_place.models import Place
from jargon.models import (Publication, PublicationStatus, RecordType,
                           ReferenceSource, Repository)
from languages_plus.models import Language
from media.models import Media
from model_utils.models import TimeStampedModel
from polymorphic.models import PolymorphicModel


class Reference(models.Model):
    source = models.ForeignKey(ReferenceSource, on_delete=models.CASCADE)
    unitid = models.CharField(max_length=128)

    def __str__(self):
        return '{}: {}'.format(self.source, self.unitid)


class Subject(models.Model):
    """TODO: UKAT"""
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


class Organisation(models.Model):
    """TODO: Organisation"""
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


@reversion.register()
class ArchivalRecord(PolymorphicModel):
    uuid = models.CharField(max_length=64, unique=True)

    repository = models.ForeignKey(Repository, on_delete=models.CASCADE)

    references = models.ManyToManyField(Reference)

    title = models.CharField(max_length=1024)
    provenance = models.TextField(blank=True, null=True)
    creation_dates = models.CharField(max_length=256)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    media = models.ManyToManyField(Media)

    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    languages = models.ManyToManyField(Language)
    extent = models.CharField(max_length=256)

    subjects = models.ManyToManyField(Subject)
    persons_as_subjects = models.ManyToManyField(Entity)
    organisations_as_subjects = models.ManyToManyField(Organisation)
    places_as_subjects = models.ManyToManyField(Place)

    related_materials = models.CharField(max_length=256, blank=True, null=True)

    cataloguer = models.CharField(max_length=512)
    description_date = models.DateField()

    rights_declaration = models.TextField()
    publication_status = models.ForeignKey(
        PublicationStatus, on_delete=models.PROTECT)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def archival_level(self):
        return self.get_real_instance_class().__name__


@reversion.register()
class ArchivalRecordSet(TimeStampedModel):
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.SET_NULL)

    title = models.CharField(max_length=256)
    description = models.TextField()
    archival_records = models.ManyToManyField(ArchivalRecord)

    def __str__(self):
        return self.title

    @property
    def number_of_records(self):
        return self.archival_records.count()


@reversion.register()
class Collection(ArchivalRecord):
    administrative_history = models.TextField()
    arrangement = models.TextField()

    def __str__(self):
        return self.title


class SeriesBase(models.Model):
    publications = models.ManyToManyField(Publication)

    class Meta:
        abstract = True


@reversion.register()
class Series(ArchivalRecord, SeriesBase):
    parent_collection = models.ForeignKey(
        Collection, blank=True, null=True, on_delete=models.CASCADE)
    parent_series = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE)

    arrangement = models.TextField()

    class Meta:
        verbose_name_plural = 'Series'

    def __str__(self):
        return self.title


class FileBase(models.Model):
    record_type = models.ManyToManyField(RecordType)

    physical_description = models.TextField(blank=True, null=True)

    copyright_status = models.CharField(max_length=256)
    publication_permission = models.TextField(blank=True, null=True)
    withheld = models.CharField(max_length=256, blank=True, null=True)

    url = models.URLField(blank=True, null=True)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


@reversion.register()
class File(ArchivalRecord, SeriesBase, FileBase):
    parent_series = models.ForeignKey(
        Series, blank=True, null=True, on_delete=models.CASCADE)
    parent_file = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE)

    creators = models.ManyToManyField(Entity, related_name='files_created')
    persons_as_relations = models.ManyToManyField(
        Entity, related_name='files_as_relations')
    places_as_relations = models.ManyToManyField(
        Place, related_name='files_as_relations')

    def __str__(self):
        return self.title


@reversion.register()
class Item(ArchivalRecord, SeriesBase, FileBase):
    parent_series = models.ForeignKey(
        Series, blank=True, null=True, on_delete=models.CASCADE)
    parent_file = models.ForeignKey(
        File, blank=True, null=True, on_delete=models.CASCADE,
        verbose_name='File')

    creators = models.ManyToManyField(Entity, related_name='items_created')
    creation_places = models.ManyToManyField(
        Place, related_name='items_created')
    persons_as_relations = models.ManyToManyField(
        Entity, related_name='items_as_relations')
    places_as_relations = models.ManyToManyField(
        Place, related_name='items_as_relations')

    def __str__(self):
        return self.title
