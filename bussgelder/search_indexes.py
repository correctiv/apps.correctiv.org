import logging

from django.conf import settings
from django.template.loader import render_to_string

from elasticsearch import (Elasticsearch, helpers as es_helpers,
                          exceptions as es_exceptions)

from .models import Fine
from .search_utils import GermanIndexAnalysis

es_logger = logging.getLogger('elasticsearch')
es_logger.addHandler(logging.StreamHandler())


def get_es():
    return Elasticsearch(settings.ELASTICSEARCH_URL)


class SearchIndex(object):
    def __init__(self, es=None):
        self.es = es or get_es()

    @property
    def queryset(self):
        return self.model._default_manager.all()

    def create(self):
        try:
            self.es.indices.delete(self.index_name)
        except es_exceptions.NotFoundError:
            pass
        self.es.indices.create(self.index_name, {
            'settings': {
                    'analysis': self.get_index_analysis()
            },
            'mappings': {
                self.name: {
                    "properties": self.get_mapping()
                }
            }
        })

    def get_documents(self):
        for obj in self.queryset.iterator():
            yield self.make_document(obj)

    def get_document_create_bulk_op(self):
        for obj in self.get_documents():
            obj.update({
                '_op_type': 'create',
                '_index': self.index_name,
                '_type': self.name,
                '_id': obj['id'],
            })
            yield obj

    def index(self):
        action_generator = self.get_document_create_bulk_op
        return es_helpers.bulk(self.es, action_generator())

    def search(self, term, size=10, offset=0):
        result = self.es.search(
            index=self.index_name,
            doc_type=self.name,
            body=self.construct_query(term),
            size=size,
            from_=offset
        )
        raw_results = result['hits']['hits']

        results = []
        for r in raw_results:
            d = r['_source']
            for key, val in r.get('highlight', {}).items():
                d[key + '_highlight'] = val[0]
            results.append(d)

        return {
            'total': result['hits']['total'],
            'results': results,
            'aggregations': result.get('aggregations', {}),
        }

    def get_mapping(self):
        raise NotImplementedError

    def get_index_analysis(self):
        raise NotImplementedError

    def make_document(self, obj):
        raise NotImplementedError


class FineIndex(GermanIndexAnalysis, SearchIndex):
    index_name = 'bussgelder'
    name = 'fines'
    model = Fine
    queryset = model._default_manager.select_related('organisation')
    aggregations = ['state']

    def construct_query(self, term):
        return {
            "query": {"query_string": {"query": term}},
            "aggs": {
                "states": {
                    "terms": {"field": "state_slug"}
                },
                "total_sum": {"sum": {"field": "amount"}}
            },
            "highlight": {
                "pre_tags": ["<span class=\"highlighted\">"],
                "post_tags": ["</span>"],
                "fields": {
                    "text": {}
                }
            },
            "sort": [
                {
                    "amount": {
                        "order": "desc"
                    }
                },
                "_score"
            ]
        }

    def get_mapping(cls):
        """Returns an Elasticsearch mapping."""

        return {
            'id': {'type': 'integer'},
            'organisation_slug': {'type': 'string', 'index': 'not_analyzed'},
            'organisation_name': {
                "type": "multi_field",
                "fields": {
                    "organisation_name": {
                        "type": "string",
                        "index": "analyzed",
                        'index_analyzer': 'text',
                        'search_analyzer': 'text'
                    },
                    "original": {"type": "string",
                                 "index": "not_analyzed"}
                }
            },
            'text': {'type': 'string', 'index': 'analyzed',
                     'index_analyzer': 'text', 'search_analyzer': 'text'},
            'state_slug': {'type': 'string', 'index': 'not_analyzed', 'store': True},
            'state_name': {'type': 'string', 'index': 'not_analyzed'},
            'department': {'type': 'string', 'index': 'not_analyzed'},
            'department_detail': {'type': 'string', 'index': 'not_analyzed'},
            'year': {'type': 'integer', 'index': 'not_analyzed', 'store': True},
            'amount': {'type': 'double', 'index': 'not_analyzed', 'store': True},
        }

    def make_document(self, obj):
        return {
            'id': obj.pk,
            'organisation_slug': obj.organisation.slug,
            'organisation_name': obj.organisation.name,
            'state_slug': obj.state,
            'state_name': obj.state_label,
            'department': obj.department,
            'department_detail': obj.department_detail,
            'year': obj.year,
            'amount': obj.amount,
            'text': render_to_string(
                'search/indexes/bussgelder/fine_text.txt',
                {'object': obj}
            )
        }
