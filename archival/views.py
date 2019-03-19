from rest_framework import filters, viewsets

from .models import ArchivalRecord, Reference
from .serializers import (ArchivalRecordPolymorphicSerializer,
                          ReferenceSerializer)


class ArchivalRecordViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ArchivalRecord.objects.order_by('id')
    serializer_class = ArchivalRecordPolymorphicSerializer
    filter_backends = (filters.OrderingFilter,)
    ordering_fields = ('title', 'start_date', 'end_date', 'creation_dates',
                       'uuid')


class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
