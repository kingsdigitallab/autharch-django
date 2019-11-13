import reversion
from authority.models import Entity
from django.conf import settings
from django.db import models
from geonames_place.models import Place
from jargon.models import (
    Publication, PublicationStatus, RecordType, ReferenceSource, Repository
)
from languages_plus.models import Language
from media.models import Media
from model_utils.models import TimeStampedModel
from polymorphic.models import PolymorphicModel

from . import constants


class Project(models.Model):
    title = models.CharField(max_length=128, unique=True)
    slug = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.title


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
    rcin = models.CharField('RCIN', max_length=256, blank=True, null=True)
    project = models.ForeignKey(Project, on_delete=models.SET_NULL, null=True,
                                help_text='Which project does this record\
                                    belong to?')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE,
                                   help_text=constants.REPOSITORY_HELP)

    references = models.ManyToManyField(Reference, blank=True,
                                        help_text=constants.REFERENCES_HELP)

    title = models.CharField(max_length=1024, help_text=constants.TITLE_HELP)

    publication_description = models.TextField(blank=True, null=True)
    provenance = models.TextField('Custodial History/Provenance', blank=True, null=True)
    creation_dates = models.CharField(max_length=1024, null=True, blank=True,
                                      help_text=constants.CREATION_DATES_HELP)
    creation_dates_notes = models.CharField(max_length=1024, null=True,
                                            blank=True)
    aquisition_dates = models.CharField(max_length=1024, null=True, blank=True)
    aquisition_dates_notes = models.CharField(max_length=1024, null=True,
                                              blank=True)

    start_date = models.DateField(blank=True, null=True,
                                  help_text=constants.START_DATE_HELP)
    end_date = models.DateField(blank=True, null=True,
                                help_text=constants.END_DATE_HELP)

    physical_location = models.CharField(max_length=2048, blank=True,
                                         null=True)

    origin_location = models.CharField(
        'location of originals', max_length=2048, blank=True, null=True)

    media = models.ManyToManyField(Media, blank=True)
    caption = models.TextField(blank=True, null=True)

    description = models.TextField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    languages = models.ManyToManyField(Language, blank=True)
    extent = models.CharField(max_length=1024, null=True)

    subjects = models.ManyToManyField(Subject, blank=True)
    persons_as_subjects = models.ManyToManyField(Entity, blank=True)
    related_entities = models.ManyToManyField(Entity, blank=True,
                                              related_name='related_entities')
    organisations_as_subjects = models.ManyToManyField(
        Organisation, blank=True)
    places_as_subjects = models.ManyToManyField(Place, blank=True)

    related_materials = models.CharField(
        max_length=2048, blank=True, null=True)

    connection_a = models.CharField(max_length=2048, blank=True, null=True,
                                    help_text="Generic Connection Text A")
    connection_b = models.CharField(max_length=2048, blank=True, null=True,
                                    help_text="Generic Connection Text B")
    connection_c = models.CharField(max_length=2048, blank=True, null=True,
                                    help_text="Generic Connection Text C")

    cataloguer = models.CharField(max_length=512, blank=True, null=True)
    description_date = models.DateField()
    # description_date = models.CharField(max_length=512, null=True)

    rights_declaration = models.TextField(
        default=settings.ARCHIVAL_RIGHTS_DECLARATION)
    publication_status = models.ForeignKey(
        PublicationStatus, on_delete=models.PROTECT)

    sources = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def archival_level(self):
        return self.get_real_instance_class().__name__


@reversion.register()
class ArchivalRecordSet(TimeStampedModel):
    project = models.ForeignKey(Project, on_delete=models.SET_NULL,
                                null=True,
                                help_text='Which project does this set\
                                    belong to?')
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

    copyright_status = models.CharField(max_length=256, blank=True)
    publication_permission = models.TextField(blank=True, null=True)
    withheld = models.CharField(max_length=256, blank=True, null=True)

    url = models.URLField('URL', blank=True, null=True)

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
    creators = models.ManyToManyField(
        Entity, blank=True, related_name='files_created')
    creation_places = models.ManyToManyField(
        Place, related_name='files_created', blank=True)
    persons_as_relations = models.ManyToManyField(
        Entity, blank=True, related_name='files_as_relations')
    places_as_relations = models.ManyToManyField(
        Place, blank=True, related_name='files_as_relations')

    def __str__(self):
        return self.title


@reversion.register()
class Item(ArchivalRecord, SeriesBase, FileBase):
    parent_series = models.ForeignKey(
        Series, blank=True, null=True, on_delete=models.CASCADE)
    parent_file = models.ForeignKey(
        File, blank=True, null=True, on_delete=models.CASCADE,
        verbose_name='File')
    creators = models.ManyToManyField(
        Entity, blank=True, related_name='items_created')
    creation_places = models.ManyToManyField(
        Place, related_name='items_created', blank=True)
    persons_as_relations = models.ManyToManyField(
        Entity, blank=True, related_name='items_as_relations')
    places_as_relations = models.ManyToManyField(
        Place, blank=True, related_name='items_as_relations')

    def __str__(self):
        return self.title
