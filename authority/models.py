import reversion
from django.db import models
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


class EntityType(TimeStampedModel):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


@reversion.register()
class Entity(TimeStampedModel):
    entity_type = models.ForeignKey(EntityType, on_delete=models.CASCADE)

    class Meta:
        verbose_name_plural = 'Entities'


@reversion.register()
class Identity(DateRangeMixin, TimeStampedModel):
    entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name='identities')

    class Meta:
        verbose_name_plural = 'Identities'

    @property
    def authorised_form(self):
        return self.name_entries.filter(authorised_form=True).first()


@reversion.register()
class NameEntry(DateRangeMixin, LanguageScriptMixin, TimeStampedModel):
    identity = models.ForeignKey(
        Identity, on_delete=models.CASCADE, related_name='name_entries')

    authorised_form = models.BooleanField()

    class Meta:
        verbose_name_plural = 'Name entries'

    def __str__(self):
        return ', '.join(['{}: {}'.format(
            p.name_part_type, p.part) for p in self.parts])


class NamePartType(TimeStampedModel):
    title = models.CharField(max_length=32, unique=True)

    def __str__(self):
        return self.title


@reversion.register()
class NamePart(TimeStampedModel):
    name_entry = models.ForeignKey(
        NameEntry, on_delete=models.CASCADE, related_name='parts')
    name_part_type = models.ForeignKey(NamePartType, on_delete=models.PROTECT)
    part = models.CharField(max_length=256)

    def __str__(self):
        return '{}: {}'.format(self.name_part_type, self.part)


class Function(TimeStampedModel):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


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

    name = models.CharField(max_length=256)
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
    place = models.CharField(max_length=256)


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


class FamilyTreeLevel(TimeStampedModel):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


@reversion.register()
class Structure(TimeStampedModel):
    description = models.ForeignKey(Description, on_delete=models.CASCADE,
                                    related_name='structures')

    level = models.ForeignKey(FamilyTreeLevel, on_delete=models.PROTECT)
    entity = models.ForeignKey(Entity, on_delete=models.CASCADE)
    citation = models.TextField(blank=True, null=True)


class EntityRelationType(TimeStampedModel):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


@reversion.register()
class Relation(DateRangeMixin, TimeStampedModel):
    entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name='relations')

    relation_type = models.ForeignKey(
        EntityRelationType, on_delete=models.PROTECT)
    place = models.CharField(max_length=256, blank=True, null=True)
    notes = models.TextField()


class ResourceType(TimeStampedModel):
    title = models.CharField(max_length=128, unique=True)

    def __str__(self):
        return self.title


@reversion.register()
class Resource(TimeStampedModel):
    entity = models.ForeignKey(
        Entity, on_delete=models.CASCADE, related_name='resources')

    resource_type = models.ForeignKey(ResourceType, on_delete=models.PROTECT)
    url = models.URLField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
