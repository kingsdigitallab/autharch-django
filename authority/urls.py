from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import EntityViewSet

router = DefaultRouter()
router.register(r'entities', EntityViewSet)

urlpatterns = [
    path('', include(router.urls))
]
