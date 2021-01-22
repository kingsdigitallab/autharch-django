from django import forms
from haystack.forms import FacetedSearchForm


class EntityFacetedSearchForm(FacetedSearchForm):

    q = forms.CharField(required=False)

    def __init__(self, *args, start_year=None, end_year=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._start_year = start_year
        self._end_year = end_year

    def no_query_found(self):
        return self.searchqueryset.all()

    def search(self):
        sqs = super().search()
        if not self.is_valid():
            return self.no_query_found()
        if self._start_year:
            sqs = sqs.filter(existence_dates__gte=self._start_year)
        if self._end_year:
            sqs = sqs.filter(existence_dates__lte=self._end_year)
        return sqs
