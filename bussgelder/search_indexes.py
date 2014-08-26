from haystack import indexes

from .models import Fine


class FineIndex(indexes.SearchIndex, indexes.Indexable):
    text = indexes.CharField(document=True, use_template=True)

    organisation_name = indexes.CharField(model_attr='organisation__name')
    organisation_slug = indexes.CharField(model_attr='organisation__slug')

    year = indexes.FacetIntegerField(model_attr='year', null=True)
    amount = indexes.DecimalField(model_attr='amount')
    state = indexes.FacetCharField(model_attr='state_label')
    # department = 

    def get_model(self):
        return Fine

    def index_queryset(self, using=None):
        """Used when the entire index for model is updated."""
        return self.get_model().objects.select_related('organisation').all()
