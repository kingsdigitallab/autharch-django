from django.shortcuts import get_object_or_404
from rest_framework import filters, viewsets
from rest_framework.response import Response

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

    def retrieve(self, request, pk=None):
        context = {'request': request}
        record = get_object_or_404(self.queryset, pk=pk)
        serializer = self.serializer_class(record, context=context)
        # Rejig the structure to group related materials together.
        data = serializer.data
        data['related'] = {}
        related_keys = [
            'subjects', 'places_as_subjects', 'persons_as_subjects',
            'organisations_as_subjects', 'related_materials', 'publications',
            'related_entities',
        ]
        for related_key in related_keys:
            related_value = data.pop(related_key, [])
            if related_value:
                data['related'][related_key] = related_value
        return Response(data)


class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
