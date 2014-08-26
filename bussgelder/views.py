from urllib import urlencode
from urlparse import urlparse, parse_qsl

from django.views.generic import ListView, DetailView

from haystack.query import SearchQuerySet
from haystack.views import FacetedSearchView

from .forms import FineSearchForm
from .models import Organisation


default_sqs = (SearchQuerySet()
                .facet('state', order='term')
)


class FineSearchView(FacetedSearchView):
    results_per_page = 15

    def extra_context(self):
        extra = super(FineSearchView, self).extra_context()
        d = dict(parse_qsl(urlparse(self.request.get_full_path()).query))
        d.pop('page', None)
        extra['getvars'] = '&' + urlencode([
            (k.encode('utf-8'), v.encode('latin1')) for k, v in d.items()])
        return extra

search = FineSearchView(form_class=FineSearchForm,
                          searchqueryset=default_sqs)


class OrganisationList(ListView):
    model = Organisation


class OrganisationDetail(DetailView):
    model = Organisation
