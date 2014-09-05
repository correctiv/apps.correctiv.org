from django.views.generic import ListView, DetailView

from .forms import OrganisationSearchForm
from .models import Organisation
from .search_indexes import OrganisationIndex
from .search_utils import SearchPaginator


class OrganisationSearchView(ListView):
    template_name = 'bussgelder/search.html'
    paginate_by = 15
    paginator_class = SearchPaginator

    def get_queryset(self):
        self.form = OrganisationSearchForm(self.request.GET)
        self.result = self.form.search(size=self.paginate_by)
        return self.result

    def get_context_data(self, **kwargs):
        context = super(OrganisationSearchView, self).get_context_data(**kwargs)
        context['result'] = self.result
        context['query'] = self.request.GET.get('q')
        context['form'] = self.form
        context['base_template'] = 'bussgelder/search_base.html'
        if self.request.GET.get('embed'):
            context['base_template'] = 'bussgelder/embed_base.html'
        return context


class OrganisationDetail(DetailView):
    model = Organisation

    def get_context_data(self, **kwargs):
        context = super(OrganisationDetail, self).get_context_data(**kwargs)
        idx = OrganisationIndex()
        context['mlt'] = idx.search(self.object.name,
                size=15, sort=False,
                aggregations=False
        )
        return context
