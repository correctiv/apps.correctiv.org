from django import forms

from .search_indexes import FineIndex
from .search_utils import SearchQueryset


class FineSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Suche',
        widget=forms.TextInput(
            attrs={
                'type': 'search',
                'class': 'form-control',
                'placeholder': 'Ihre Sucheingabe'
            }))

    def no_query_found(self, idx, size):
        return SearchQueryset(
            idx,
            '*',
            size=size
        )

    def search(self, size=None):
        idx = FineIndex()

        if not self.is_valid():
            return self.no_query_found(idx, size)

        if not self.cleaned_data.get('q'):
            return self.no_query_found(idx, size)

        sqs = SearchQueryset(
            idx,
            self.cleaned_data.get('q'),
            size=size
        )

        return sqs
