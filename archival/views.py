from rest_framework import filters, viewsets

from .models import ArchivalRecord, Reference
from .serializers import (ArchivalRecordPolymorphicSerializer,
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


class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
