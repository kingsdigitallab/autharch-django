from django.conf import settings
from django.db import models

import reversion
from authority.fields import PartialDateField
from authority.models import Entity
from controlled_vocabulary.models import (
    ControlledTermField, ControlledTermsField)
from geonames_place.models import Place
from jargon.models import (
    Function, MaintenanceStatus, PublicationStatus, RecordType,
    ReferenceSource, Repository
)
from media.models import Media
from model_utils.models import TimeStampedModel
from polymorphic.models import PolymorphicModel
from script_codes.models import Script

from . import constants


class Project(models.Model):
    title = models.CharField(max_length=128, unique=True)
    slug = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.title


class Reference(models.Model):
    source = models.ForeignKey(ReferenceSource, on_delete=models.CASCADE)
    unitid = models.CharField(max_length=512)

    def __str__(self):
        return '{}: {}'.format(self.source, self.unitid)


@reversion.register(follow=['origin_locations', 'referenced_related_materials',
                            'transcription_images', 'transcription_texts'])
class ArchivalRecord(PolymorphicModel, TimeStampedModel):
    uuid = models.CharField(max_length=64, unique=True)
    rcin = models.CharField('RCIN', max_length=256, blank=True, null=True,
                            help_text=constants.RCIN_HELP)
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, blank=True, null=True,
        help_text='Which project does this record belong to?')
    repository = models.ForeignKey(Repository, on_delete=models.CASCADE,
                                   help_text=constants.REPOSITORY_HELP)

    references = models.ManyToManyField(Reference, blank=True)
    calm_reference = models.CharField(
        blank=True, max_length=64, null=True, unique=True,
        verbose_name='CALM reference')

    title = models.CharField(max_length=1024, help_text=constants.TITLE_HELP)

    publication_description = models.TextField(blank=True, null=True)
    provenance = models.TextField(
        'Custodial History/Provenance', blank=True,
        help_text=constants.CUSTODIAL_HISTORY_PROVENANCE_HELP)
    creation_dates = models.CharField(
        max_length=1024, null=True, blank=True,
        help_text=constants.CREATION_DATES_HELP)
    creation_dates_notes = models.CharField(max_length=1024, null=True,
                                            blank=True)

    aquisition_dates = models.CharField(max_length=1024, null=True, blank=True)
    aquisition_dates_notes = models.CharField(max_length=1024, null=True,
                                              blank=True)

    start_date = PartialDateField(help_text=constants.START_DATE_HELP)
    end_date = PartialDateField(blank=True,
                                help_text=constants.END_DATE_HELP)

    physical_location = models.CharField(max_length=2048, blank=True,
                                         null=True)

    media = models.ManyToManyField(Media, blank=True)
    caption = models.TextField(blank=True, null=True)

    description = models.TextField(blank=True, null=True,
                                   help_text=constants.DESCRIPTION_HELP)
    notes = models.TextField(blank=True, null=True,
                             help_text=constants.NOTES_HELP)
    languages = ControlledTermsField(['iso639-2'], blank=True,
                                     help_text=constants.LANGUAGES_HELP)
    extent = models.CharField(max_length=1024, null=True,
                              help_text=constants.EXTENT_HELP)

    subjects = models.ManyToManyField(Function, blank=True,
                                      related_name='record_subjects')
    persons_as_subjects = models.ManyToManyField(
        Entity, blank=True, limit_choices_to={'entity_type__title': 'person'},
        related_name='person_subject_for_records')
    related_entities = models.ManyToManyField(Entity, blank=True,
                                              related_name='related_entities')
    organisations_as_subjects = models.ManyToManyField(
        Entity, blank=True, verbose_name='Corporate bodies as subjects',
        limit_choices_to={'entity_type__title': 'corporateBody'},
        related_name='organisation_subject_for_records')
    places_as_subjects = models.ManyToManyField(Place, blank=True)

    connection_a = models.CharField(max_length=2048, blank=True, null=True,
                                    help_text="Generic Connection Text A")
    connection_b = models.CharField(max_length=2048, blank=True, null=True,
                                    help_text="Generic Connection Text B")
    connection_c = models.CharField(max_length=2048, blank=True, null=True,
                                    help_text="Generic Connection Text C")

    rights_declaration = models.TextField(
        default=settings.ARCHIVAL_RIGHTS_DECLARATION)
    rights_declaration_abbreviation = models.CharField(
        max_length=256, blank=True)
    rights_declaration_citation = models.URLField(blank=True)
    maintenance_status = models.ForeignKey(
        MaintenanceStatus, on_delete=models.PROTECT)
    publication_status = models.ForeignKey(
        PublicationStatus, on_delete=models.PROTECT)
    language = ControlledTermField(['iso639-2'], on_delete=models.PROTECT,
                                   related_name='record_control_languages',
                                   verbose_name="Record language")
    script = models.ForeignKey(Script, on_delete=models.PROTECT,
                               related_name='record_control_scripts',
                               verbose_name="Record script")

    sources = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    @property
    def archival_level(self):
        return self.get_real_instance_class().__name__

    def is_deleted(self):
        return self.maintenance_status.title == 'deleted'


@reversion.register()
class ArchivalRecordSet(TimeStampedModel):
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True,
        help_text='Which project does this set belong to?')
    author = models.ForeignKey(
        settings.AUTH_USER_MODEL, blank=True, null=True,
        on_delete=models.SET_NULL)

    title = models.CharField(max_length=256, help_text=constants.TITLE_HELP)
    description = models.TextField()
    archival_records = models.ManyToManyField(ArchivalRecord)

    def __str__(self):
        return self.title

    @property
    def number_of_records(self):
        return self.archival_records.count()


@reversion.register(follow=['archivalrecord_ptr'])
class Collection(ArchivalRecord):
    administrative_history = models.TextField(
        help_text=constants.ADMINISTRATIVE_HISTORY_HELP)
    arrangement = models.TextField(
        blank=True, help_text=constants.ARRANGEMENT_HELP)

    def __str__(self):
        return self.title


class SeriesBase(models.Model):
    publications = models.TextField(
        blank=True, verbose_name="Known previous publications",
        help_text=constants.PUBLICATIONS_HELP)

    class Meta:
        abstract = True


@reversion.register(follow=['archivalrecord_ptr'])
class Series(ArchivalRecord, SeriesBase):
    parent_collection = models.ForeignKey(
        Collection, blank=True, null=True, on_delete=models.CASCADE)
    parent_series = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE)

    arrangement = models.TextField(
        blank=True, help_text=constants.ARRANGEMENT_HELP)

    class Meta:
        verbose_name_plural = 'Series'

    def __str__(self):
        return self.title


class FileBase(models.Model):
    record_type = models.ManyToManyField(
        RecordType, help_text=constants.RECORD_TYPE_HELP)

    physical_description = models.TextField(
        blank=True, null=True, help_text=constants.PHYSICAL_DESCRIPTION_HELP)

    copyright_status = models.CharField(
        max_length=256, blank=True, help_text=constants.COPYRIGHT_STATUS_HELP,
        verbose_name='Copyright')
    publication_permission = models.TextField(
        'Credit', blank=True, null=True, help_text=constants.CREDIT_HELP)
    withheld = models.CharField(max_length=256, blank=True, null=True,
                                help_text=constants.WITHHELD_HELP)

    url = models.URLField('URL', blank=True, null=True,
                          help_text=constants.URL_HELP)

    class Meta:
        abstract = True

    def __str__(self):
        return self.title


@reversion.register(follow=['archivalrecord_ptr'])
class File(ArchivalRecord, SeriesBase, FileBase):
    parent_collection = models.ForeignKey(
        Collection, blank=True, null=True, on_delete=models.CASCADE)
    parent_series = models.ForeignKey(
        Series, blank=True, null=True, on_delete=models.CASCADE)
    parent_file = models.ForeignKey(
        'self', blank=True, null=True, on_delete=models.CASCADE)
    creators = models.ManyToManyField(
        Entity, verbose_name="Writer", blank=True,
        related_name='files_created', help_text=constants.WRITER_HELP)
    creation_places = models.ManyToManyField(
        Place, verbose_name="Place of writing", related_name='files_created',
        blank=True, help_text=constants.PLACE_OF_WRITING_HELP)
    persons_as_relations = models.ManyToManyField(
        Entity, verbose_name="Addressee", blank=True,
        related_name='files_as_relations')
    places_as_relations = models.ManyToManyField(
        Place, verbose_name="Receiving address", blank=True,
        related_name='files_as_relations',
        help_text=constants.PLACE_OF_WRITING_HELP)

    def __str__(self):
        return self.title


@reversion.register(follow=['archivalrecord_ptr'])
class Item(ArchivalRecord, SeriesBase, FileBase):
    parent_collection = models.ForeignKey(
        Collection, blank=True, null=True, on_delete=models.CASCADE)
    parent_series = models.ForeignKey(
        Series, blank=True, null=True, on_delete=models.CASCADE)
    parent_file = models.ForeignKey(
        File, blank=True, null=True, on_delete=models.CASCADE,
        verbose_name='File')
    creators = models.ManyToManyField(
        Entity, verbose_name="Writer", blank=True,
        related_name='items_created')
    creation_places = models.ManyToManyField(
        Place, verbose_name="Place of writing", related_name='items_created',
        blank=True, help_text=constants.PLACE_OF_WRITING_HELP)
    persons_as_relations = models.ManyToManyField(
        Entity, verbose_name="Addressee", blank=True,
        related_name='items_as_relations')
    places_as_relations = models.ManyToManyField(
        Place, verbose_name="Receiving address", blank=True,
        related_name='items_as_relations',
        help_text=constants.PLACE_OF_WRITING_HELP)

    def __str__(self):
        return self.title


@reversion.register()
class ArchivalRecordTranscription(models.Model):
    record = models.ForeignKey(ArchivalRecord, on_delete=models.CASCADE,
                               related_name='transcription_texts')
    transcription = models.TextField(blank=True)
    order = models.PositiveIntegerField()
    transcriber = models.CharField(blank=True, max_length=128)
    reviewer = models.CharField(blank=True, max_length=128)
    corrector = models.CharField(blank=True, max_length=128)

    class Meta:
        ordering = ['order']
        unique_together = (('record', 'order'),)


@reversion.register()
class ArchivalRecordImage(models.Model):
    record = models.ForeignKey(ArchivalRecord, on_delete=models.CASCADE,
                               related_name='transcription_images')
    image = models.ImageField(upload_to='ar_transcription_images/')
    order = models.PositiveIntegerField()

    class Meta:
        ordering = ['order']
        unique_together = (('record', 'order'),)


@reversion.register()
class OriginLocation(models.Model):
    record = models.ForeignKey(ArchivalRecord, on_delete=models.CASCADE,
                               related_name='origin_locations')
    location = models.CharField(
        blank=True, verbose_name='location of originals', max_length=256,
        help_text=constants.LOCATION_OF_ORIGINALS_HELP)


@reversion.register()
class RelatedMaterialReference(models.Model):
    record = models.ForeignKey(ArchivalRecord, on_delete=models.CASCADE,
                               related_name='referenced_related_materials')
    context = models.CharField(
        max_length=2048, help_text=constants.RELATED_MATERIALS_LABEL_HELP,
        verbose_name="Related material label")
    related_record = models.ForeignKey(
        ArchivalRecord, on_delete=models.CASCADE,
        related_name='referencing_related_materials',
        verbose_name="Related material")


@reversion.register()
class ObjectGroup(TimeStampedModel):
    title = models.CharField(max_length=100)
    slug = models.SlugField(verbose_name='URL slug')
    introduction = models.TextField(blank=True)
    description = models.TextField(blank=True)
    collections = models.ManyToManyField(
        Collection, blank=True, related_name='relating_group')
    records = models.ManyToManyField(
        ArchivalRecord, blank=True, related_name='featuring_group', verbose_name='Featured archival records')
    related_entities = models.ManyToManyField(
        Entity, blank=True, related_name='relating_group')
    featured_entities = models.ManyToManyField(
        Entity, blank=True, related_name='featuring_group')
    is_deleted = models.BooleanField(default=False)

    def __str__(self):
        return self.title
