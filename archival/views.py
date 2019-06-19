from rest_framework import filters, viewsets

from .models import ArchivalRecord, Reference, Project
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

    def get_queryset(self):
        """
        This enables filtering of the queryset defined in the Viewset
        by Project slug.

        Returns: self.queryset filtered by project slug. If no slug is
        provided, all records are returned. If an invalid
        slug is provided, an empty queryset is returned.
        """
        project_slug = self.request.query_params.get('project', None)
        if project_slug is not None:
            try:
                project = Project.objects.get(slug=project_slug)
                return self.queryset.filter(project=project)
            except Project.DoesNotExist:
                # Invalid project, don't return anything!
                return self.queryset.none()
        else:
            return self.queryset


class ReferenceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Reference.objects.all()
    serializer_class = ReferenceSerializer
