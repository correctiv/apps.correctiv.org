from django import forms

from .search_indexes import OrganisationIndex
from .search_utils import SearchQueryset
from .models import GERMAN_STATES


class OrganisationSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Suche',
        widget=forms.TextInput(
            attrs={
                'type': 'search',
                'class': 'form-control',
                'placeholder': 'Ihre Sucheingabe'
            }))

    amount_gte = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput)

    amount_lte = forms.IntegerField(
        required=False,
        widget=forms.HiddenInput)

    state = forms.ChoiceField(
        choices=GERMAN_STATES,
        required=False,
        widget=forms.HiddenInput)

    year = forms.TypedChoiceField(
        choices=(
            (2011, '2011'),
            (2012, '2012'),
            (2013, '2013')
        ),
        required=False,
        coerce=int,
        empty_value='',
        widget=forms.HiddenInput)

    sort = forms.ChoiceField(
        choices=(
            # ('name:asc', 'Name'),
            ('amount:desc', 'Betrag'),
            ('', 'Relevanz')
        ),
        initial='amount:desc',
        required=False,
        widget=forms.RadioSelect)

    FILTERS = {
        'state': 'state',
        'year': 'year'
    }
    RANGES = (
        'amount_lte',
        'amount_gte'
    )

    def _search(self, idx, size, query):
        return SearchQueryset(
            idx,
            query,
            filters=self.get_filters(),
            ranges=self.get_ranges(),
            sort=self.cleaned_data.get('sort', ''),
            size=size
        )

    def no_query_found(self, idx, size):
        return self._search(idx, size, '')

    def get_filters(self):
        filters = {}
        for key in self.FILTERS:
            filters[self.FILTERS[key]] = self.cleaned_data[key]
        return filters

    def get_ranges(self):
        return {key: self.cleaned_data[key] for key in self.RANGES}

    def search(self, size=None):
        idx = OrganisationIndex()
        if not self.is_valid():
            return SearchQueryset(idx, '')

        if not self.cleaned_data.get('q'):
            return self.no_query_found(idx, size)

        sqs = self._search(idx, size, self.cleaned_data['q'])

        return sqs
