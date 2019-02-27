from rest_framework import generics

from .models import PublicationStatus, ReferenceSource, Repository
from .serializers import (PublicationStatusSerializer,
                          ReferenceSourceSerializer, RepositorySerializer)


class PublicationStatusDetail(generics.RetrieveAPIView):
    queryset = PublicationStatus.objects.all()
    serializer_class = PublicationStatusSerializer


class ReferenceSourceDetail(generics.RetrieveAPIView):
    queryset = ReferenceSource.objects.all()
    serializer_class = ReferenceSourceSerializer


class RepositoryDetail(generics.RetrieveAPIView):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
