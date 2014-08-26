from django import forms

from haystack.forms import FacetedSearchForm


class FineSearchForm(FacetedSearchForm):
    q = forms.CharField(
        required=False,
        label='Suche',
        widget=forms.TextInput(
            attrs={
                'type': 'search',
                'class': 'form-control',
                'placeholder': 'Ihre Sucheingabe'
            }))

    def search(self):
        return super(FineSearchForm, self).search().highlight()

    def no_query_found(self):
        """
        Determines the behavior when no query was found.

        By default, no results are returned (``EmptySearchQuerySet``).

        Should you want to show all results, override this method in your
        own ``SearchForm`` subclass and do ``return self.searchqueryset.all()``.
        """
        return self.searchqueryset.all().order_by('-amount')
