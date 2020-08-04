from haystack import indexes

from archival.models import Collection, File, Item, Series
from authority.models import Entity, Relation
from jargon.models import ReferenceSource


RA_REFERENCE_SOURCE = ReferenceSource.objects.get(title='RA')


# The polymorphic ArchivalRecord model subclasses must have their own
# index, and fields cannot be inherited. However, data preparation
# methods may be inherited.

class ArchivalRecordIndex:

    def _get_year_from_date(self, date):
        if not date:
            year = None
        else:
            try:
                year_end_index = date.index('-')
                year = int(date[:year_end_index])
            except ValueError:
                year = int(date)
        return year

    def prepare_addressees(self, obj):
        return list(obj.persons_as_relations.distinct().values_list(
            'pk', flat=True))

    def prepare_dates(self, obj):
        start_year = self._get_year_from_date(obj.start_date)
        end_year = self._get_year_from_date(obj.end_date)
        if start_year is None:
            years = []
        elif end_year is None:
            years = [start_year]
        else:
            years = list(range(start_year, end_year + 1))
        return years

    def prepare_description(self, obj):
        return str(obj)

    def prepare_languages(self, obj):
        return list(obj.languages.distinct().values_list('label', flat=True))

    def prepare_ra_references(self, obj):
        return list(obj.references.filter(source=RA_REFERENCE_SOURCE)
                    .values_list('unitid', flat=True))

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

    def get_model(self):
        return Collection


class FileIndex(indexes.SearchIndex, indexes.Indexable, ArchivalRecordIndex):

    text = indexes.CharField(document=True, use_template=True)
    archival_level = indexes.CharField(model_attr='archival_level',
                                       faceted=True)
    publication_status = indexes.CharField(model_attr='publication_status')
    maintenance_status = indexes.CharField(model_attr='maintenance_status')
    addressees = indexes.MultiValueField(faceted=True)
    dates = indexes.MultiValueField()
    creation_date = indexes.CharField(model_attr='creation_dates', null=True)
    languages = indexes.MultiValueField(faceted=True)
    writers = indexes.MultiValueField(faceted=True)
    writers_display = indexes.CharField()
    modified = indexes.DateTimeField(model_attr='modified')
    description = indexes.CharField()
    ra_references = indexes.MultiValueField()
    record_types = indexes.MultiValueField(
        faceted=True, model_attr='record_type__title')

    def get_model(self):
        return File


class ItemIndex(indexes.SearchIndex, indexes.Indexable, ArchivalRecordIndex):

    text = indexes.CharField(document=True, use_template=True)
    archival_level = indexes.CharField(model_attr='archival_level',
                                       faceted=True)
    publication_status = indexes.CharField(model_attr='publication_status')
    maintenance_status = indexes.CharField(model_attr='maintenance_status')
    addressees = indexes.MultiValueField(faceted=True)
    dates = indexes.MultiValueField()
    creation_date = indexes.CharField(model_attr='creation_dates', null=True)
    languages = indexes.MultiValueField(faceted=True)
    writers = indexes.MultiValueField(faceted=True)
    writers_display = indexes.CharField()
    modified = indexes.DateTimeField(model_attr='modified')
    description = indexes.CharField()
    ra_references = indexes.MultiValueField()

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
    ra_references = indexes.MultiValueField()

    def get_model(self):
        return Entity

    def prepare_description(self, obj):
        return str(obj)

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
