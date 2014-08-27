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
    state = forms.ChoiceField(
        choices=GERMAN_STATES,
        required=False,
        widget=forms.HiddenInput)

    year = forms.TypedChoiceField(
        choices=((2013, '2013'),),
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
        initial='',
        required=False,
        widget=forms.RadioSelect)

    FILTERS = {
        'state': 'state',
        'year': 'year'
    }

    def _search(self, idx, size, query):
        return SearchQueryset(
            idx,
            query,
            filters=self.get_filters(),
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

    def search(self, size=None):
        idx = OrganisationIndex()

        if not self.is_valid():
            return self.no_query_found(idx, size)

        if not self.cleaned_data.get('q'):
            return self.no_query_found(idx, size)

        sqs = self._search(idx, size, self.cleaned_data['q'])

        return sqs
