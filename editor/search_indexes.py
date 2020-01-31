from haystack import indexes

from archival.models import Collection, File, Item, Series
from authority.models import Entity


# The polymorphic ArchivalRecord model subclasses must have their own
# index.

class CollectionIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    archival_level = indexes.CharField(model_attr='archival_level',
                                       faceted=True)
    publication_status = indexes.CharField(model_attr='publication_status')
    description = indexes.CharField()

    def get_model(self):
        return Collection

    def prepare_description(self, obj):
        return str(obj)


class FileIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    archival_level = indexes.CharField(model_attr='archival_level',
                                       faceted=True)
    publication_status = indexes.CharField(model_attr='publication_status')
    writers = indexes.MultiValueField(faceted=True)
    description = indexes.CharField()

    def get_model(self):
        return File

    def prepare_description(self, obj):
        return str(obj)

    def prepare_writers(self, obj):
        return list(obj.creators.distinct().values_list('pk', flat=True))


class ItemIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    archival_level = indexes.CharField(model_attr='archival_level',
                                       faceted=True)
    publication_status = indexes.CharField(model_attr='publication_status')
    description = indexes.CharField()

    def get_model(self):
        return Item

    def prepare_description(self, obj):
        return str(obj)


class SeriesIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    archival_level = indexes.CharField(model_attr='archival_level',
                                       faceted=True)
    publication_status = indexes.CharField(model_attr='publication_status')
    description = indexes.CharField()

    def get_model(self):
        return Series

    def prepare_description(self, obj):
        return str(obj)


class EntityIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    entity_type = indexes.CharField(model_attr='entity_type__title',
                                    faceted=True)
    modified = indexes.DateTimeField(model_attr='modified')
    description = indexes.CharField()

    def get_model(self):
        return Entity

    def prepare_description(self, obj):
        return str(obj)
