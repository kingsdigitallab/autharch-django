from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from .models import Entity
from .serializers import EntitySerializer


class EntityViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Entity.objects.order_by('-modified')
    serializer_class = EntitySerializer

    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['entity_type__title']
