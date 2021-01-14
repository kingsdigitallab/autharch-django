from django.shortcuts import get_object_or_404
from haystack.query import SearchQuerySet
from rest_framework import filters, viewsets
from rest_framework.response import Response

from authority.models import Entity

from .models import ArchivalRecord, Collection, File, Item, Reference, Series
from .serializers import (
    ArchivalRecordPolymorphicSerializer, ArchivalRecordListSerializer,
    ReferenceSerializer)


class ArchivalRecordViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to list or view archival records.

    list:
    Return a list of all the archival records. The `ordering` parameter
    accepts the following values: id, title, start_date, end_date,
    creation_dates. By default the archival records are ordered by *id*.

    read:
    Return the given archival record.
    """
    queryset = ArchivalRecord.objects.order_by('id')
    serializer_class = ArchivalRecordPolymorphicSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('title', 'start_date', 'end_date', 'creation_dates',
                       'id')

    def _annotate_facets(self, facets):
        if not facets:
            return facets
        for facet, values in facets.items():
            # Some facet field values are a model object ID, so get
            # a display string for them.
            display_values = None
            if facet in ('persons_as_relations', 'writers'):
                display_values = Entity.objects.filter(
                    id__in=[value[0] for value in values])
            new_values = []
            for value_data in values:
                obj_id, obj_count = value_data
                new_value = {'key': obj_id, 'doc_count': obj_count,
                             'label': obj_id}
                if display_values is not None:
                    new_value['label'] = str(display_values.get(id=obj_id))
                new_values.append(new_value)
            facets[facet] = new_values
        return facets

    def list(self, request):
        queryset = SearchQuerySet().models(
            Collection, File, Item, Series).exclude(
                maintenance_status='deleted').facet('archival_level').facet(
                    'languages', size=0).facet('record_types', size=0).facet(
                        'writers', size=0).facet('persons_as_relations',
                                                 size=0)
        serializer = ArchivalRecordListSerializer(queryset, many=True)
        facet_data = self._annotate_facets(queryset.facet_counts()['fields'])
        data = {
            'count': len(queryset),
            'facets': facet_data,
            'results': serializer.data,
        }
        return Response(data)

    def retrieve(self, request, pk=None):
        context = {'request': request}
        record = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(record, context=context)
        # Rejig the structure to group related materials together.
        data = serializer.data
        data['related'] = {}
        related_keys = [
            'subjects', 'places_as_subjects', 'persons_as_subjects',
            'organisations_as_subjects', 'related_materials', 'publications',
            'related_entities',
        ]
        for related_key in related_keys:
            related_value = data.pop(related_key, [])
            if related_value:
                data['related'][related_key] = related_value
        return Response(data)


class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
