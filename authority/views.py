import re

from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from haystack.query import SearchQuerySet

from controlled_vocabulary.models import ControlledTerm
from geonames_place.models import Place as GeoPlace
from jargon.models import Gender

from .forms import EntityFacetedSearchForm
from .models import Entity, Identity
from .serializers import EntitySerializer, EntityListSerializer


class EntityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to list or view entity records.

    list:
    Return a list of all the entities. The `entity_type_title` parameter
    accepts the following values: Person, Family, Organisation.

    read:
    Return the given entity.
    """
    queryset = Entity.objects.order_by('-modified')
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entity_type__title']

    def _annotate_facets(self, facets):
        if not facets:
            return facets
        for facet, values in facets.items():
            # Some facet field values are a model object ID, so get
            # a display string for them.
            display_values = None
            if facet == 'related_entities':
                display_values = Entity.objects.filter(
                    id__in=[value[0] for value in values])
            elif facet == 'related_places':
                display_values = GeoPlace.objects.filter(
                    id__in=[value[0] for value in values])
            elif facet == 'genders':
                display_values = Gender.objects.filter(
                    id__in=[value[0] for value in values])
            elif facet == 'languages':
                display_values = ControlledTerm.objects.filter(
                    id__in=[value[0] for value in values])
            new_values = []
            for value_data in values:
                obj_id, obj_count = value_data
                new_value = {'key': obj_id, 'doc_count': obj_count,
                             'label': obj_id}
                if display_values is not None:
                    new_value['label'] = str(display_values.get(id=obj_id))
                # Only include the positive side of
                # has_multiple_identities and has_royal_name.
                if facet in ('has_multiple_identities', 'has_royal_name') and \
                   obj_id != 1:
                    continue
                new_values.append(new_value)
            facets[facet] = new_values
        return facets

    def _assemble_existence_years(self, existence_years):
        start_year = None
        end_year = None
        if isinstance(existence_years, str):
            match = re.fullmatch(r'(\d{0,4}),(\d{0,4})', existence_years)
            if match is not None:
                start_year = match.group(1)
                end_year = match.group(2)
        return start_year, end_year

    def _assemble_selected_facets(self, params, facet_fields):
        selected_facets = []
        for facet, values in params.lists():
            if facet in facet_fields:
                for value in values:
                    selected_facets.append('{}:{}'.format(facet, value))
        return selected_facets

    def _get_existence_year_range(self):
        identities = Identity.objects.filter(preferred_identity=True)
        start_dates = identities.exclude(date_from='').values_list(
            'date_from', flat=True)
        if len(start_dates) == 0:
            years = [0, 2040]
            return years
        min_year = sorted(start_dates, key=lambda x: x[:4])[0][:4]
        end_dates = identities.exclude(date_to='').values_list(
            'date_to', flat=True)
        if not end_dates:
            end_dates = start_dates
        max_year = sorted(end_dates, key=lambda x: x[:4], reverse=True)[0][:4]
        return [int(min_year), int(max_year)]

    def list(self, request):
        facet_fields = [
            'entity_type', 'genders', 'has_multiple_identities',
            'has_royal_name', 'languages', 'related_entities',
            'related_places'
        ]
        queryset = SearchQuerySet().models(Entity).exclude(
            maintenance_status='deleted')
        for facet_field in facet_fields:
            queryset = queryset.facet(facet_field, size=0)
        selected_facets = self._assemble_selected_facets(
            request.GET, facet_fields)
        start_year, end_year = self._assemble_existence_years(
            request.GET.get('existence_years', None))
        form = EntityFacetedSearchForm(
            request.GET, searchqueryset=queryset,
            selected_facets=selected_facets, start_year=start_year,
            end_year=end_year)
        if form.is_valid():
            queryset = form.search()
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = EntityListSerializer(page, many=True)
            response = self.get_paginated_response(serializer.data)
        else:
            serializer = EntityListSerializer(queryset, many=True)
            response = Response(serializer.data)
        facet_data = self._annotate_facets(queryset.facet_counts()['fields'])
        facet_data['existence_years'] = self._get_existence_year_range()
        response.data['facets'] = facet_data
        return response

    def retrieve(self, request, pk=None):
        context = {'request': request}
        queryset = Entity.objects.order_by('-modified')
        entity = get_object_or_404(queryset, pk=pk)
        serializer = EntitySerializer(entity, context=context)
        return Response(serializer.data)
