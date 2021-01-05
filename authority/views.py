from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import Entity
from .serializers import EntitySerializer


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
    serializer_class = EntitySerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entity_type__title']
