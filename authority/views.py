from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from haystack.query import SearchQuerySet

from controlled_vocabulary.models import ControlledTerm
from geonames_place.models import Place as GeoPlace
from jargon.models import Gender

from .models import Entity
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

    def list(self, request):
        queryset = SearchQuerySet().models(Entity).facet('entity_type').facet(
            'genders').facet('languages').facet(
                'has_multiple_identities').facet(
                'related_entities', size=0).facet(
                    'related_places', size=0).facet('has_royal_name')
        serializer = EntityListSerializer(queryset, many=True)
        facet_data = self._annotate_facets(queryset.facet_counts()['fields'])
        data = {
            'count': len(queryset),
            'facets': facet_data,
            'results': serializer.data,
        }
        return Response(data)

    def retrieve(self, request, pk=None):
        context = {'request': request}
        queryset = Entity.objects.order_by('-modified')
        entity = get_object_or_404(queryset, pk=pk)
        serializer = EntitySerializer(entity, context=context)
        return Response(serializer.data)
