from haystack import indexes

from archival.models import Collection, File, Item, Series
from authority.models import Entity


# The polymorphic ArchivalRecord model subclasses must have their own
# index.

class CollectionIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    record_type = indexes.CharField(faceted=True)

    def get_model(self):
        return Collection

    def prepare_record_type(self, obj):
        return 'Collection'


class FileIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    record_type = indexes.CharField(faceted=True)

    def get_model(self):
        return File

    def prepare_record_type(self, obj):
        return 'File'


class ItemIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    record_type = indexes.CharField(faceted=True)

    def get_model(self):
        return Item

    def prepare_record_type(self, obj):
        return 'Item'


class SeriesIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    record_type = indexes.CharField(faceted=True)

    def get_model(self):
        return Series

    def prepare_record_type(self, obj):
        return 'Series'


class EntityIndex(indexes.SearchIndex, indexes.Indexable):

    text = indexes.CharField(document=True, use_template=True)
    entity_type = indexes.CharField(model_attr='entity_type__title',
                                    faceted=True)

    def get_model(self):
        return Entity
