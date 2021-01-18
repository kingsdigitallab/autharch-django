from django.shortcuts import get_object_or_404
from haystack.query import SearchQuerySet
from rest_framework import filters, viewsets
from rest_framework.response import Response

from authority.models import Entity

from .forms import ArchivalRecordFacetedSearchForm
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

    def _assemble_selected_facets(self, params, facet_fields):
        selected_facets = []
        for facet, values in params.lists():
            if facet in facet_fields:
                for value in values:
                    selected_facets.append('{}:{}'.format(facet, value))
        return selected_facets

    def list(self, request):
        facet_fields = ['archival_level', 'languages', 'record_types',
                        'writers', 'persons_as_relations']
        queryset = SearchQuerySet().models(
            Collection, File, Item, Series).exclude(
                maintenance_status='deleted')
        for facet_field in facet_fields:
            queryset = queryset.facet(facet_field, size=0)
        selected_facets = self._assemble_selected_facets(
            request.GET, facet_fields)
        form = ArchivalRecordFacetedSearchForm(
            request.GET, searchqueryset=queryset,
            selected_facets=selected_facets)
        if form.is_valid():
            queryset = form.search()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = ArchivalRecordListSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = ArchivalRecordListSerializer(queryset, many=True)
            response = Response(serializer.data)
        facet_data = self._annotate_facets(queryset.facet_counts()['fields'])
        facet_data['creation_years'] = [1700, 2020]
        response.data['facets'] = facet_data
        return response

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
