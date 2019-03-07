from rest_framework import viewsets

from .models import PublicationStatus, ReferenceSource, Repository
from .serializers import (PublicationStatusSerializer,
                          ReferenceSourceSerializer, RepositorySerializer)


class PublicationStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PublicationStatus.objects.all()
    serializer_class = PublicationStatusSerializer


class ReferenceSourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReferenceSource.objects.all()
    serializer_class = ReferenceSourceSerializer


class RepositoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
