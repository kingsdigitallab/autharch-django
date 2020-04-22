from django.urls import path
# from rest_framework.routers import DefaultRouter

from . import views

# from .views import (PublicationStatusViewSet, ReferenceSourceViewSet,
#                     RepositoryViewSet)

# router = DefaultRouter()
# router.register(r'publicationstatuses', PublicationStatusViewSet)
# router.register(r'referencesources', ReferenceSourceViewSet)
# router.register(r'repositories', RepositoryViewSet)

app_name = 'jargon'
urlpatterns = [
    path('jargon_function_autocomplete/',
         views.FunctionAutocompleteJsonView.as_view(),
         name='jargon_function_autocomplete'),
    path('jargon_gender_autocomplete/',
         views.GenderAutocompleteJsonView.as_view(),
         name='jargon_gender_autocomplete'),
]
