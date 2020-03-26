from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

from geonames_place.models import Place as GeoPlace
from jargon.models import (
    EntityRelationType, EntityType, Function, MaintenanceStatus, NamePartType,
    PublicationStatus, ResourceRelationType
)
from languages_plus.models import Language
from model_utils.models import TimeStampedModel
import reversion
from script_codes.models import Script

from . import constants


class DateRangeMixin(models.Model):
    date_from = models.DateField(blank=True, null=True,
                                 help_text=constants.START_DATE_HELP)
    date_to = models.DateField(blank=True, null=True,
                               help_text=constants.END_DATE_HELP)
    display_date = models.CharField(max_length=1024, null=True, blank=True)

    class Meta:
        abstract = True

    def get_date(self):
        dates = self.__dict__

        if self.date_from:
            if self.date_to:
                return '{date_from} - {date_to}'.format(**dates)

            return '{date_from} - '.format(**dates)

        if self.date_to:
            return ' - {date_to}'.format(**dates)

        return 'Unknown'


class LanguageScriptMixin(models.Model):
    language = models.ForeignKey(
        Language, on_delete=models.PROTECT,
        help_text=constants.LANGUAGE_HELP)
    script = models.ForeignKey(Script, on_delete=models.PROTECT)

    class Meta:
        abstract = True


@reversion.register()
class Entity(TimeStampedModel, DateRangeMixin):
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE)
    project = models.ForeignKey(
        'archival.Project', on_delete=models.SET_NULL, blank=True, null=True,
        help_text='Which project does this record belong to?')

    objects = models.Manager()

    class Meta:
        verbose_name_plural = 'Entities'

    def __str__(self):
        return self.display_name

    @property
    def display_name(self):
        try:
            return self.identities.order_by(
                '-preferred_identity').first().authorised_form.display_name
        except AttributeError:
            return 'Unnamed object'

    def get_all_name_entries(self):
        return NameEntry.objects.filter(identity__entity=self)

    @staticmethod
    def get_or_create_by_display_name(name, language, script, project=None):
        if not name or not language or not script:
            return None, False

        name_entries = NameEntry.objects.filter(display_name=name)

        if project:
            name_entries = name_entries.filter(
                identity__entity__project=project)
        # too many entities match the display name, we can't accurately return
        # one
        if name_entries and name_entries.count() > 1:
            return None, False

        if name_entries and name_entries.count() == 1:
            return name_entries[0].identity.entity, False

        et, _ = EntityType.objects.get_or_create(title='person')

        entity = Entity(entity_type=et)
        entity.save()

        identity = Identity(entity=entity)
        identity.date_from = timezone.now()
        identity.preferred_identity = True
        identity.save()

        name_entry = NameEntry(identity=identity)
        name_entry.display_name = name
        name_entry.authorised_form = True
        name_entry.date_from = identity.date_from
        name_entry.language = language
        name_entry.script = script
        name_entry.save()

        control = Control(entity=entity)
        control.language = language
        control.script = script
        ms, _ = MaintenanceStatus.objects.get_or_create(title='new')
        ps, _ = PublicationStatus.objects.get_or_create(title='inProcess')
        control.maintenance_status = ms
        control.publication_status = ps
        control.save()

        return entity, True

    def is_deleted(self):
        return self.control.maintenance_status.title == 'deleted'


@reversion.register()
class Identity(DateRangeMixin, TimeStampedModel):
    entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name='identities')

    preferred_identity = models.BooleanField()

    class Meta:
        verbose_name_plural = 'Identities'

    def __str__(self):
        try:
            return self.authorised_form.display_name
        except AttributeError:
            return 'Unsaved object'

    @property
    def authorised_form(self):
        return self.name_entries.order_by('-authorised_form').first()


@reversion.register()
class NameEntry(DateRangeMixin, LanguageScriptMixin, TimeStampedModel):
    identity = models.ForeignKey(
        Identity, on_delete=models.CASCADE, related_name='name_entries')

    display_name = models.CharField(max_length=2048)
    authorised_form = models.BooleanField()
    is_royal_name = models.BooleanField(default=False)

    class Meta:
        verbose_name_plural = 'Name entries'

    def __str__(self):
        return self.display_name or ', '.join(['{}: {}'.format(
            p.name_part_type, p.part) for p in self.parts.all()])

    def clean(self):
        # A royal name must have at least a "forename" name part
        # and a "properTitle" name part.
        if self.is_royal_name:
            forename_type = NamePartType.objects.get(title='forename')
            proper_title_type = NamePartType.objects.get(title='properTitle')
            if not self.parts.filter(name_part_type=forename_type) and \
               not self.parts.filter(name_part_type=proper_title_type):
                raise ValidationError(
                    'A royal name must contain a "forename" part and a '
                    '"properTitle" part.')


@reversion.register()
class NamePart(TimeStampedModel):
    name_entry = models.ForeignKey(
        NameEntry, on_delete=models.CASCADE, related_name='parts')
    name_part_type = models.ForeignKey(NamePartType, on_delete=models.PROTECT)
    part = models.CharField(max_length=256)

    def __str__(self):
        return '{}: {}'.format(self.name_part_type, self.part)


@reversion.register()
class Description(DateRangeMixin, TimeStampedModel):
    identity = models.ForeignKey(
        Identity, on_delete=models.CASCADE, related_name='descriptions')


@reversion.register()
class Place(DateRangeMixin, TimeStampedModel):
    description = models.ForeignKey(
        Description, on_delete=models.CASCADE, related_name='places')

    place = models.ForeignKey(GeoPlace, on_delete=models.CASCADE)
    address = models.TextField(null=True)
    role = models.TextField(null=True, help_text=constants.PLACE_ROLE_HELP)


@reversion.register()
class LanguageScript(LanguageScriptMixin, TimeStampedModel):
    description = models.ForeignKey(Description, on_delete=models.CASCADE,
                                    related_name='languages_scripts')


@reversion.register()
class BiographyHistory(TimeStampedModel):
    description = models.OneToOneField(Description, on_delete=models.CASCADE,
                                       related_name='biography_history')

    abstract = models.TextField(null=True,
                                help_text=constants.BIOGRAPHY_ABSTRACT_HELP)
    content = models.TextField(blank=True, null=True)
    structure_or_genealogy = models.TextField(
        blank=True, null=True,
        help_text=constants.BIOGRAPHY_STRUCTURE_GENEALOGY_HELP)
    sources = models.TextField(blank=True, null=True)
    copyright = models.TextField(blank=True, null=True,
                                 help_text=constants.BIOGRAPHY_COPYRIGHT_HELP)

    class Meta:
        verbose_name = 'Biography/History'
        verbose_name_plural = 'Biography/History'


@reversion.register()
class Event(DateRangeMixin, TimeStampedModel):
    description = models.ForeignKey(
        Description, on_delete=models.CASCADE, related_name='events')

    event = models.TextField()
    place = models.ForeignKey(GeoPlace, on_delete=models.CASCADE)


@reversion.register()
class LocalDescription(DateRangeMixin, TimeStampedModel):
    description = models.ForeignKey(Description, on_delete=models.CASCADE,
                                    related_name='local_descriptions')
    gender = models.CharField(max_length=256, help_text=constants.GENDER_HELP)
    notes = models.TextField(verbose_name='Descriptive notes', blank=True)
    citation = models.TextField(blank=True)


@reversion.register()
class Mandate(DateRangeMixin, TimeStampedModel):
    description = models.ForeignKey(Description, on_delete=models.CASCADE,
                                    related_name='mandates')

    term = models.CharField(max_length=256, blank=True)
    notes = models.TextField(verbose_name="Descriptive Notes", blank=True,
                             null=True)
    citation = models.TextField(blank=True, null=True)


@reversion.register()
class Function(DateRangeMixin, TimeStampedModel):
    description = models.ForeignKey(Description, on_delete=models.CASCADE,
                                    related_name='functions')
    title = models.ForeignKey(Function, verbose_name="Function",
                              on_delete=models.CASCADE)


@reversion.register()
class LegalStatus(DateRangeMixin, TimeStampedModel):
    description = models.ForeignKey(Description, on_delete=models.CASCADE,
                                    related_name='legal_statuses')

    term = models.CharField(max_length=256, blank=True)
    notes = models.TextField(verbose_name="Descriptive Notes", blank=True,
                             null=True)
    citation = models.TextField(blank=True, null=True,
                                help_text=constants.LEGAL_STATUS_CITATION_HELP)

    class Meta:
        verbose_name_plural = 'Legal status'


@reversion.register()
class Relation(DateRangeMixin, TimeStampedModel):
    identity = models.ForeignKey(
        Identity, on_delete=models.CASCADE, related_name='relations')
    relation_type = models.ForeignKey(
        EntityRelationType, verbose_name="Relationship type",
        on_delete=models.PROTECT)
    related_entity = models.ForeignKey(
        Entity, verbose_name="Related person or corporate body",
        on_delete=models.CASCADE, null=True,
        related_name='related_to_relations')
    relation_detail = models.TextField(verbose_name="Description", null=True)
    place = models.ForeignKey(
        GeoPlace, verbose_name="Place related to relationship", blank=True,
        null=True, on_delete=models.CASCADE)
    notes = models.TextField()


@reversion.register()
class Resource(TimeStampedModel):
    identity = models.ForeignKey(
        Identity, on_delete=models.CASCADE, related_name='resources')
    relation_type = models.ForeignKey(
        ResourceRelationType, verbose_name="Resource relationship type",
        on_delete=models.PROTECT,
        help_text=constants.RESOURCE_RELATIONSHIP_TYPE_HELP)
    url = models.URLField(verbose_name="URL", null=True)
    citation = models.TextField()
    notes = models.TextField(null=True)


@reversion.register()
class Control(LanguageScriptMixin, TimeStampedModel):
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE,
                                  related_name="control")

    maintenance_status = models.ForeignKey(
        MaintenanceStatus, on_delete=models.PROTECT)
    publication_status = models.ForeignKey(
        PublicationStatus, on_delete=models.PROTECT)

    rights_declaration = models.TextField(
        default=settings.AUTHORITY_RIGHTS_DECLARATION)
    rights_declaration_abbreviation = models.CharField(
        max_length=256, blank=True)
    rights_declaration_citation = models.URLField(blank=True)

    class Meta:
        verbose_name_plural = 'Control'


@reversion.register()
class Source(TimeStampedModel):
    control = models.ForeignKey(Control, on_delete=models.CASCADE,
                                related_name="sources")

    name = models.CharField(max_length=256)
    url = models.URLField(verbose_name="URL", blank=True, null=True)
    notes = models.TextField(null=True)
