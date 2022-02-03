from haystack import indexes

from archival.models import Collection, File, Item, ObjectGroup, Series
from authority.models import (
    Entity, LanguageScript, LocalDescription, NameEntry, Place, Relation)
from jargon.models import ReferenceSource


def _get_year_from_date(date):
    if not date:
        year = None
    else:
        try:
            year_end_index = date.index('-')
            year = int(date[:year_end_index])
        except ValueError:
            year = int(date)
    return year


def _get_year_range(start_date, end_date):
    start_year = _get_year_from_date(start_date)
    end_year = _get_year_from_date(end_date)
    if start_year is None:
        years = []
    elif end_year is None:
        years = [start_year]
    else:
        years = list(range(start_year, end_year + 1))
    return years


# The polymorphic ArchivalRecord model subclasses must have their own
# index, and fields cannot be inherited. However, data preparation
# methods may be inherited.

class ArchivalRecordIndex:

    def prepare_dates(self, obj):
        return _get_year_range(obj.start_date, obj.end_date)

    def prepare_description(self, obj):
        return str(obj)

    def prepare_languages(self, obj):
        return list(obj.languages.distinct().values_list('label', flat=True))

    def prepare_persons_as_relations(self, obj):
        return list(obj.persons_as_relations.distinct().values_list(
            'pk', flat=True))

    def prepare_ra_references(self, obj):
        source = ReferenceSource.objects.get(title='RA')
        return list(obj.references.filter(source=source).values_list(
            'unitid', flat=True))

    def prepare_transcription_text(self, obj):
        if obj.transcription_texts.count():
            return True

    def prepare_writers(self, obj):
        return list(obj.creators.distinct().values_list('pk', flat=True))

    def prepare_writers_display(self, obj):
        display_forms = []
        for writer in obj.creators.distinct():
            display_forms.append(writer.display_name)
        return ', '.join(display_forms)


class CollectionIndex(indexes.SearchIndex, indexes.Indexable,
                      ArchivalRecordIndex):

    text = indexes.CharField(document=True, use_template=True)
    archival_level = indexes.CharField(model_attr='archival_level',
                                       faceted=True)
    publication_status = indexes.CharField(model_attr='publication_status')
    maintenance_status = indexes.CharField(model_attr='maintenance_status')
    dates = indexes.MultiValueField()
    creation_date = indexes.CharField(model_attr='creation_dates', null=True)
    languages = indexes.MultiValueField(faceted=True)
    modified = indexes.DateTimeField(model_attr='modified')
    description = indexes.CharField()
    ra_references = indexes.MultiValueField()
    transcription_text = indexes.BooleanField(faceted=True)

    def get_model(self):
        return Collection


class FileIndex(indexes.SearchIndex, indexes.Indexable, ArchivalRecordIndex):

    text = indexes.CharField(document=True, use_template=True)
    archival_level = indexes.CharField(model_attr='archival_level',
                                       faceted=True)
    publication_status = indexes.CharField(model_attr='publication_status')
    maintenance_status = indexes.CharField(model_attr='maintenance_status')
    dates = indexes.MultiValueField()
    creation_date = indexes.CharField(model_attr='creation_dates', null=True)
    languages = indexes.MultiValueField(faceted=True)
    writers = indexes.MultiValueField(faceted=True)
    writers_display = indexes.CharField()
    persons_as_relations = indexes.MultiValueField(faceted=True)
    modified = indexes.DateTimeField(model_attr='modified')
    description = indexes.CharField()
    ra_references = indexes.MultiValueField()
    record_types = indexes.MultiValueField(
        faceted=True, model_attr='record_type__title')
    transcription_text = indexes.BooleanField(faceted=True)

    def get_model(self):
        return File


class ItemIndex(indexes.SearchIndex, indexes.Indexable, ArchivalRecordIndex):

    text = indexes.CharField(document=True, use_template=True)
    archival_level = indexes.CharField(model_attr='archival_level',
                                       faceted=True)
    publication_status = indexes.CharField(model_attr='publication_status')
    maintenance_status = indexes.CharField(model_attr='maintenance_status')
    dates = indexes.MultiValueField()
    creation_date = indexes.CharField(model_attr='creation_dates', null=True)
    languages = indexes.MultiValueField(faceted=True)
    writers = indexes.MultiValueField(faceted=True)
    writers_display = indexes.CharField()
    persons_as_relations = indexes.MultiValueField(faceted=True)
    modified = indexes.DateTimeField(model_attr='modified')
    description = indexes.CharField()
    ra_references = indexes.MultiValueField()
    record_types = indexes.MultiValueField(
        faceted=True, model_attr='record_type__title')
    transcription_text = indexes.BooleanField(faceted=True)

    def get_model(self):
        return Item


class SeriesIndex(indexes.SearchIndex, indexes.Indexable, ArchivalRecordIndex):

    text = indexes.CharField(document=True, use_template=True)
    archival_level = indexes.CharField(model_attr='archival_level',
                                       faceted=True)
    publication_status = indexes.CharField(model_attr='publication_status')
    maintenance_status = indexes.CharField(model_attr='maintenance_status')
    dates = indexes.MultiValueField()
    creation_date = indexes.CharField(model_attr='creation_dates', null=True)
    languages = indexes.MultiValueField(faceted=True)
    modified = indexes.DateTimeField(model_attr='modified')
    description = indexes.CharField()
    ra_references = indexes.MultiValueField()
    transcription_text = indexes.BooleanField(faceted=True)

    def get_model(self):
        return Series


class EntityIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    entity_type = indexes.CharField(model_attr='entity_type__title',
                                    faceted=True)
    publication_status = indexes.CharField()
    maintenance_status = indexes.CharField()
    modified = indexes.DateTimeField(model_attr='modified')
    description = indexes.CharField()
    related_entities = indexes.MultiValueField(faceted=True)
    related_places = indexes.MultiValueField(faceted=True)
    ra_references = indexes.MultiValueField()
    genders = indexes.MultiValueField(faceted=True)
    languages = indexes.MultiValueField(faceted=True)
    has_multiple_identities = indexes.BooleanField(faceted=True)
    has_royal_name = indexes.BooleanField(faceted=True)
    existence_dates = indexes.MultiValueField()

    def get_model(self):
        return Entity

    def prepare_description(self, obj):
        return str(obj)

    def prepare_existence_dates(self, obj):
        # Use the existence dates of the primary identity only.
        try:
            identity = obj.identities.filter(preferred_identity=True)[0]
        except IndexError:
            return []
        return _get_year_range(identity.date_from, identity.date_to)

    def prepare_genders(self, obj):
        return [ld.gender.pk for ld in LocalDescription.objects.filter(
            description__identity__entity=obj)]

    def prepare_has_multiple_identities(self, obj):
        has = False
        if obj.identities.count() > 1:
            has = True
        return has

    def prepare_has_royal_name(self, obj):
        has = False
        if NameEntry.objects.filter(is_royal_name=True).filter(
                identity__entity=obj).count() > 0:
            has = True
        return has

    def prepare_languages(self, obj):
        return [ls.language.pk for ls in LanguageScript.objects.filter(
            description__identity__entity=obj)]

    def prepare_maintenance_status(self, obj):
        try:
            return obj.control.maintenance_status.title
        except AttributeError:
            return ''

    def prepare_publication_status(self, obj):
        try:
            return obj.control.publication_status.title
        except AttributeError:
            return ''

    def prepare_related_entities(self, obj):
        return [relation.related_entity.pk for relation in
                Relation.objects.filter(identity__entity=obj)
                if relation.related_entity]

    def prepare_related_places(self, obj):
        return [place.place.pk for place in Place.objects.filter(
            description__identity__entity=obj)]


class ObjectGroupIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, model_attr='title')
    description = indexes.CharField(model_attr='title')
    maintenance_status = indexes.CharField()
    modified = indexes.DateTimeField(model_attr='modified')

    def get_model(self):
        return ObjectGroup

    def prepare_maintenance_status(self, obj):
        if obj.is_deleted:
            return 'deleted'
        return 'revised'
