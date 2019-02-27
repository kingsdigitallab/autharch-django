from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns

from .views import (ArchivalRecordDetail, ArchivalRecordList, CollectionDetail,
                    CollectionList, ReferenceDetail)

urlpatterns = [
    path('collections/', CollectionList.as_view()),
    path('collections/<int:pk>/', CollectionDetail.as_view(),
         name='collection-detail'),
    path('records/', ArchivalRecordList.as_view()),
    path('records/<int:pk>/', ArchivalRecordDetail.as_view(),
         name='archivalrecord-detail'),
    path('references/<int:pk>/', ReferenceDetail.as_view(),
         name='reference-detail')
]

urlpatterns = format_suffix_patterns(urlpatterns)
