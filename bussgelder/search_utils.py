from django.utils import six
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.db.models.query import QuerySet


class SearchPaginator(Paginator):
    def validate_number(self, number):
        """
        Validates the given 1-based page number.
        """
        try:
            number = int(number)
        except (TypeError, ValueError):
            raise PageNotAnInteger('That page number is not an integer')
        if number < 1:
            raise EmptyPage('That page number is less than 1')
        return number

    def page(self, number):
        """
        Don't evaluate orphans before slicing
        """
        number = self.validate_number(number)
        bottom = (number - 1) * self.per_page
        top = bottom + self.per_page
        return self._get_page(self.object_list[bottom:top], number, self)


class SearchQueryset(QuerySet):
    def __init__(self, index, query, **kwargs):
        self.index = index
        self.query = query
        self.size = kwargs.pop('size')
        self.default_size = self.size
        self.kwargs = kwargs
        self.start = 0
        self._total = None
        self._results = None
        self._result_cache = None

    def _fetch_all(self):
        self._results = self.index.search(
            self.query,
            size=self.size,
            offset=self.start,
            **self.kwargs
        )
        self._total = self._results['total']
        self._result_cache = self._results['results']

    def aggregations(self):
        if self._results is None:
            self._fetch_all()
        return self._results['aggregations']

    def count(self):
        if self._total is None:
            self._fetch_all()
        return self._total

    def __iter__(self):
        self._fetch_all()
        return iter(self._result_cache)

    def __getitem__(self, k):
        """
        Retrieves an item or slice from the set of results.
        """
        if not isinstance(k, (slice,) + six.integer_types):
            raise TypeError
        assert ((not isinstance(k, slice) and (k >= 0))
                or (isinstance(k, slice) and (k.start is None or k.start >= 0)
                    and (k.stop is None or k.stop >= 0))), \
                "Negative indexing is not supported."

        if self._result_cache is not None:
            return self._result_cache[k]

        if isinstance(k, slice):
            if k.start is not None:
                self.start = int(k.start)
            else:
                self.start = 0
            if k.stop is not None:
                self.size = int(k.stop) - self.start
            else:
                self.size = self.default_size
            self._fetch_all()
            return self._result_cache

        self.start = k
        self.size = 1
        self._fetch_all()
        return self._result_cache[0]


class GermanIndexAnalysis(object):
    def get_index_analysis(self):
        return {
            "char_filter": {
                "german_char_filter": {
                    "type": "mapping",
                    "mappings": [ "\\u00DF => ss"]
                }
            },
            "filter": {
                "german_stop": {
                    "type": "stop",
                    "stopwords": "_german_"
                },
                "custom_stop": {
                    "type": "stop",
                    "stopwords": ["e.V."]
                },
                "german_stemmer": {
                    "type": "stemmer",
                    "language": "light_german"
                },
                'unique_stem': {
                    'type': 'unique',
                    'only_on_same_position': True
                },
                "decomp": {
                  "type" : "decompound"
                }
            },
            'analyzer': {
                "german": {
                    "type": "custom",
                    "tokenizer":  "standard",
                    "char_filter": ["german_char_filter"],
                    "filter": [
                        "lowercase",
                        "keyword_repeat",
                        "german_stop",
                        "custom_stop",
                        "word_delimiter",
                        "decomp",
                        "german_normalization",
                        "german_stemmer",
                        "unique_stem"
                    ]
                }
            }
        }
