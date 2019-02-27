from rest_framework import generics

from .models import ArchivalRecord, Collection, Reference
from .serializers import (ArchivalRecordSerializer, CollectionSerializer,
                          ReferenceSerializer)


class ArchivalRecordList(generics.ListAPIView):
    queryset = ArchivalRecord.objects.all()
    serializer_class = ArchivalRecordSerializer


class ArchivalRecordDetail(generics.RetrieveAPIView):
    queryset = ArchivalRecord.objects.all()
    serializer_class = ArchivalRecordSerializer


class CollectionList(generics.ListAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


class CollectionDetail(generics.RetrieveAPIView):
    queryset = Collection.objects.all()
    serializer_class = CollectionSerializer


class ReferenceDetail(generics.RetrieveAPIView):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
