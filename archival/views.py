from rest_framework import viewsets

from .models import ArchivalRecord, Reference
from .serializers import (ArchivalRecordPolymorphicSerializer,
                          ReferenceSerializer)


class ArchivalRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArchivalRecord.objects.order_by('id')
    serializer_class = ArchivalRecordPolymorphicSerializer


class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
