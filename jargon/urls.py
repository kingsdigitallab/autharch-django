from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (PublicationStatusDetail, ReferenceSourceDetail,
                    RepositoryDetail)

urlpatterns = [
    path('publicationstatuses/<int:pk>/', PublicationStatusDetail.as_view(),
         name='publicationstatus-detail'),
    path('repositories/<int:pk>/', ReferenceSourceDetail.as_view(),
         name='referencesource-detail'),
    path('repositories/<int:pk>/', RepositoryDetail.as_view(),
         name='repository-detail'),
]

urlpatterns = format_suffix_patterns(urlpatterns)
