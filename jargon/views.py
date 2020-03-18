from django.core.paginator import Paginator
from django.db.models import Q
from django.http import JsonResponse
from django.views.generic.list import BaseListView

from rest_framework import viewsets

from .models import Function, PublicationStatus, ReferenceSource, Repository
from .serializers import (PublicationStatusSerializer,
                          ReferenceSourceSerializer, RepositorySerializer)


class FunctionAutocompleteJsonView(BaseListView):

    """View to provide autocompletion search results for Function objects.

    Adapted from django.contrib.admin.views.autocomplete and
    django.contrib.admin.options.

    """

    paginate_by = 20

    def get(self, request, *args, **kwargs):
        """Return a JsonResponse with search results of the form:

        {
            results: [{id: "123", text: "foo"}],
            pagination: {more: true}
        }

        """
        self.term = request.GET.get('term', '')
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse({
            'results': [
                {'id': str(obj.pk), 'text': str(obj)}
                for obj in context['object_list']
            ],
            'pagination': {'more': context['page_obj'].has_next()},
        })

    def get_paginator(self, queryset, per_page, orphans=0,
                      allow_empty_first_page=True):
        return Paginator(queryset, per_page, orphans, allow_empty_first_page)

    def get_queryset(self):
        qs = Function.objects.get_queryset().filter(is_term=True)
        for bit in self.term.split():
            qs = qs.filter(Q(title__icontains=bit) |
                           Q(alt_labels__icontains=bit))
        return qs.distinct().order_by('title')


class PublicationStatusViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PublicationStatus.objects.all()
    serializer_class = PublicationStatusSerializer


class ReferenceSourceViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = ReferenceSource.objects.all()
    serializer_class = ReferenceSourceSerializer


class RepositoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Repository.objects.all()
    serializer_class = RepositorySerializer
