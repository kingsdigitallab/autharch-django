import reversion
from django.db import models
from django.utils import timezone
from geonames_place.models import Place as GeoPlace
from jargon.models import (EntityRelationType, EntityType, FamilyTreeLevel,
                           Function, MaintenanceStatus, NamePartType,
                           PublicationStatus, ResourceRelationType)
from languages_plus.models import Language
from model_utils.models import TimeStampedModel
from script_codes.models import Script


class DateRangeMixin(models.Model):
    date_from = models.DateField()
    date_to = models.DateField(blank=True, null=True)

    class Meta:
        abstract = True


class LanguageScriptMixin(models.Model):
    language = models.ForeignKey(Language, on_delete=models.PROTECT)
    script = models.ForeignKey(Script, on_delete=models.PROTECT)

    class Meta:
        abstract = True


@reversion.register()
class Entity(TimeStampedModel):
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Entities'

    def __str__(self):
        return self.identities.filter(
            preferred_identity=True).first().authorised_form.display_name

    @staticmethod
    def get_or_create_by_display_name(
            name, language=Language.objects.get(name_en='English'),
            script=Script.objects.get(name='Latin')):

        if not name:
            return None

        name_entries = NameEntry.objects.filter(display_name=name)

        # too many entities match the display name, we can't accurately return
        # one
        if name_entries and name_entries.count() > 1:
            return None

        if name_entries and name_entries.count() == 1:
            return name_entries[0].identity.entity

        et, _ = EntityType.objects.get_or_create(title='Person')

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

        return entity


@reversion.register()
class Identity(DateRangeMixin, TimeStampedModel):
    entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name='identities')

    preferred_identity = models.BooleanField()

    class Meta:
        verbose_name_plural = 'Identities'

    @property
    def authorised_form(self):
        return self.name_entries.filter(authorised_form=True).first()


@reversion.register()
class NameEntry(DateRangeMixin, LanguageScriptMixin, TimeStampedModel):
    identity = models.ForeignKey(
        Identity, on_delete=models.CASCADE, related_name='name_entries')

    display_name = models.CharField(max_length=512)
    authorised_form = models.BooleanField()

    class Meta:
        verbose_name_plural = 'Name entries'

    def __str__(self):
        return ', '.join(['{}: {}'.format(
            p.name_part_type, p.part) for p in self.parts])


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
    entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name='descriptions')

    function = models.ManyToManyField(Function)

    structure_or_genealogy = models.TextField(blank=True, null=True)


@reversion.register()
class Place(DateRangeMixin, TimeStampedModel):
    description = models.ForeignKey(
        Description, on_delete=models.CASCADE, related_name='places')

    place = models.ForeignKey(GeoPlace, on_delete=models.CASCADE)
    address = models.TextField(blank=True, null=True)
    role = models.TextField(blank=True, null=True)


@reversion.register()
class LanguageScript(LanguageScriptMixin, TimeStampedModel):
    description = models.ForeignKey(Description, on_delete=models.CASCADE,
                                    related_name='languages_scripts')


@reversion.register()
class BiographyHistory(TimeStampedModel):
    description = models.OneToOneField(Description, on_delete=models.CASCADE)

    abstract = models.TextField(blank=True, null=True)
    content = models.TextField(blank=True, null=True)
    sources = models.TextField(blank=True, null=True)
    copyright = models.TextField(blank=True, null=True)

    class Meta:
        verbose_name = 'Biography/History'
        verbose_name_plural = 'Biography/History'


@reversion.register()
class Event(DateRangeMixin, TimeStampedModel):
    biography_history = models.ForeignKey(
        BiographyHistory, on_delete=models.CASCADE)

    event = models.TextField()
    place = models.ForeignKey(GeoPlace, on_delete=models.CASCADE)


@reversion.register()
class LocalDescription(DateRangeMixin, TimeStampedModel):
    description = models.ForeignKey(Description, on_delete=models.CASCADE,
                                    related_name='local_descriptions')

    gender = models.CharField(max_length=256)
    notes = models.TextField()
    citation = models.TextField()


@reversion.register()
class Mandate(DateRangeMixin, TimeStampedModel):
    description = models.ForeignKey(Description, on_delete=models.CASCADE,
                                    related_name='mandates')

    term = models.CharField(max_length=256, blank=True)
    notes = models.TextField(blank=True, null=True)
    citation = models.TextField(blank=True, null=True)


@reversion.register()
class LegalStatus(DateRangeMixin, TimeStampedModel):
    description = models.ForeignKey(Description, on_delete=models.CASCADE,
                                    related_name='legal_statuses')

    term = models.CharField(max_length=256, blank=True)
    notes = models.TextField(blank=True, null=True)
    citation = models.TextField(blank=True, null=True)


@reversion.register()
class Structure(TimeStampedModel):
    description = models.ForeignKey(Description, on_delete=models.CASCADE,
                                    related_name='structures')

    level = models.ForeignKey(FamilyTreeLevel, on_delete=models.PROTECT)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    citation = models.TextField(blank=True, null=True)


@reversion.register()
class Relation(DateRangeMixin, TimeStampedModel):
    entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name='relations')

    relation_type = models.ForeignKey(
        EntityRelationType, on_delete=models.PROTECT)
    related_entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name='related_to_relations')
    place = models.ForeignKey(
        GeoPlace, blank=True, null=True, on_delete=models.CASCADE)
    notes = models.TextField()


@reversion.register()
class Resource(TimeStampedModel):
    entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name='resources')

    relation_type = models.ForeignKey(
        ResourceRelationType, on_delete=models.PROTECT)
    url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)


@reversion.register()
class Control(LanguageScriptMixin, TimeStampedModel):
    entity = models.OneToOneField(Entity, on_delete=models.CASCADE)

    maintenance_status = models.ForeignKey(
        MaintenanceStatus, on_delete=models.PROTECT)
    publication_status = models.ForeignKey(
        PublicationStatus, on_delete=models.PROTECT)

    rights_declaration = models.TextField()

    class Meta:
        verbose_name_plural = 'Control'


@reversion.register()
class Source(TimeStampedModel):
    control = models.ForeignKey(Control, on_delete=models.CASCADE)

    name = models.CharField(max_length=256)
    url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
