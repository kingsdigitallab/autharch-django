from rest_framework import viewsets

from .models import Media
from .serializers import MediaPolymorphicSerializer


class MediaViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint to list or view media objects.

    list:
    Return a list of all the media objects. By default the archival records are
    ordered by most recently modified.

    read:
    Return the given media object.
    """
    queryset = Media.objects.order_by('modified')
    serializer_class = MediaPolymorphicSerializer
