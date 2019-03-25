from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import ArchivalRecordViewSet

router = DefaultRouter()
router.register(r'records', ArchivalRecordViewSet)
# router.register(r'references', ReferenceViewSet)

urlpatterns = [
    path('', include(router.urls))
]
