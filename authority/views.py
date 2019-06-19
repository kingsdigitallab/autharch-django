from rest_framework import viewsets
from django_filters.rest_framework import DjangoFilterBackend

from archival.models import Project
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
