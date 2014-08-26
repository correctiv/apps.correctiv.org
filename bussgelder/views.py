from urllib import urlencode
from urlparse import urlparse, parse_qsl

from django.views.generic import ListView, DetailView

from .forms import FineSearchForm
from .models import Organisation
from .search_utils import SearchPaginator


class FineSearchView(ListView):
    template_name = 'bussgelder/search.html'
    paginate_by = 15
    paginator_class = SearchPaginator

    def get_queryset(self):
        self.form = FineSearchForm(self.request.GET)
        self.result = self.form.search(size=self.paginate_by)
        return self.result

    def get_context_data(self, **kwargs):
        context = super(FineSearchView, self).get_context_data(**kwargs)
        d = dict(parse_qsl(urlparse(self.request.get_full_path()).query))
        d.pop('page', None)
        context['result'] = self.result
        context['query'] = self.request.GET.get('q')
        context['form'] = self.form
        context['getvars'] = '&' + urlencode([
            (k.encode('utf-8'), v.encode('latin1')) for k, v in d.items()])
        # import pdb; pdb.set_trace()
        return context


class OrganisationList(ListView):
    model = Organisation


class OrganisationDetail(DetailView):
    model = Organisation
