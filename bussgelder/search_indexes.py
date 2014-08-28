import logging
from urlparse import urlparse

from django.conf import settings
from django.template.loader import render_to_string

from elasticsearch import (Elasticsearch, helpers as es_helpers,
                          exceptions as es_exceptions)

from .models import Organisation
from .search_utils import GermanIndexAnalysis

es_logger = logging.getLogger('elasticsearch')
es_logger.addHandler(logging.StreamHandler())


def get_es():
    o = urlparse(settings.ELASTICSEARCH_URL)
    if o.port is None:
        port = 443 if o.scheme == 'https' else 80
    else:
        port = o.port
    return Elasticsearch([
        {'host': o.hostname, 'port': port, 'use_ssl': o.scheme == 'https'},
    ])


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

    def mlt(self, docid):
        result = self.es.mlt(
            index=self.index_name,
            doc_type=self.name,
            id=docid
        )
        return {
            'results': [r['_source'] for r in result['hits']['hits']]
        }

    def search(self, term, filters=None, size=10, offset=0, **kwargs):
        result = self.es.search(
            index=self.index_name,
            doc_type=self.name,
            body=self.construct_query(term, filters=filters, **kwargs),
            size=size,
            from_=offset
        )
        raw_results = result['hits']['hits']

        results = []
        for r in raw_results:
            d = r['_source']
            for key, val in r.get('highlight', {}).items():
                key = key.replace('.', '_')
                d[key + '_highlight'] = val[0]
            results.append(d)

        return {
            'total': result['hits']['total'],
            'results': results,
            'aggregations': result.get('aggregations', {}),
        }

    def construct_query(self, term, filters=None, **kwargs):
        query = {
            "query": {
                "query_string": {
                    "query": term,
                    "default_operator": "AND"
                }
            }
        }
        return query

    def get_mapping(self):
        return {}

    def get_index_analysis(self):
        return {}

    def make_document(self, obj):
        raise NotImplementedError


class OrganisationIndex(SearchIndex):
    index_name = 'bussgelder'
    name = 'organisations'
    model = Organisation
    queryset = model._default_manager.select_related('fines')
    aggregations = ['state']

    def construct_query(self, term, **kwargs):
        if not term:
            query = {
                "query": {"match_all": {}}
            }
        else:
            query = {
                "query": {
                    "bool": {
                        "should": [{
                            "multi_match": {
                                "query": term,
                                "fields": ["name^2"],
                                "operator": "AND"
                            }
                        }, {
                            "nested": {
                                "path": "fines",
                                "query": {
                                    "multi_match": {
                                        "fields": ["name^2", "text"],
                                        "query": term,
                                        "operator": "AND"
                                    }
                                }
                            }
                        }]
                    }
                }
            }

        query.update({
            "aggs": {
                "fines": {
                    "nested": {
                        "path": "fines"
                    },
                    "aggs": {
                        "states": {
                            "terms": {
                                "field": "fines.state",
                                "size": 0
                            }
                        },
                        "years": {
                            "terms": {
                                "field": "fines.year",
                                "size": 0
                            }
                        }
                    }
                },
                "total_sum": {"sum": {"field": "amount"}},
            },
            "highlight": {
                "pre_tags": ["<mark>"],
                "post_tags": ["</mark>"],
                "fields": {
                    "fines.text": {}
                }
            }
        })
        sort = kwargs.get('sort', 'amount:desc')
        if sort:
            sort_list = []
            name, order = sort.split(':')
            if sort:
                sort_list.append({
                    name: {
                        "order": order
                    }
                })
            sort_list.append("_score")
            query.update({"sort": sort_list})
        filters = kwargs.get('filters', {})
        if filters and any(filters.values()):
            query.update({
                'post_filter': {
                    "nested": {
                        "path": "fines",
                        "filter": {
                            "and": [{
                                "term": {'fines.' + key: value}
                            } for key, value in filters.items() if value]
                        }
                    }
                }
            })
        return query

    def get_mapping(cls):
        """Returns an Elasticsearch mapping."""

        return {
            'id': {'type': 'integer'},
            'slug': {'type': 'string', 'index': 'not_analyzed'},
            'name': {
                "type": "multi_field",
                "fields": {
                    "name": {
                        "type": "string",
                        "index": "analyzed",
                        'index_analyzer': 'german',
                        'search_analyzer': 'german'
                    },
                    "original": {"type": "string",
                                 "index": "not_analyzed"}
                }
            },
            'amount': {'type': 'double', 'index': 'not_analyzed', 'store': True},
            'fines': {
                "type": "nested",
                "properties": {
                    'id': {'type': 'integer'},
                    'name'
                    'amount': {'type': 'double', 'index': 'not_analyzed', 'store': True},
                    'name': {
                        "type": "multi_field",
                        "fields": {
                            "name": {
                                "type": "string",
                                "index": "analyzed",
                                'index_analyzer': 'german',
                                'search_analyzer': 'german'
                            },
                            "original": {"type": "string",
                                         "index": "not_analyzed"}
                        }
                    },
                    'state': {'type': 'string', 'index': 'not_analyzed', 'store': True},
                    'state_name': {'type': 'string', 'index': 'not_analyzed'},
                    'department': {'type': 'string', 'index': 'not_analyzed'},
                    'department_detail': {'type': 'string', 'index': 'not_analyzed'},
                    'year': {'type': 'integer', 'index': 'not_analyzed', 'store': True},
                    'text': {'type': 'string', 'index': 'analyzed',
                             'index_analyzer': 'german', 'search_analyzer': 'german'},

                }
            }
        }

    def make_document(self, obj):
        return {
            'id': obj.pk,
            'slug': obj.slug,
            'name': obj.name,
            'amount': obj.sum_fines,
            'fines': [{
                'id': f.pk,
                'state': f.state,
                'name': f.original_name,
                'state_name': f.state_label,
                'department': f.department,
                'department_detail': f.department_detail,
                'year': f.year,
                'amount': f.amount,
                'text': render_to_string(
                    'search/indexes/bussgelder/fine_text.txt', {'object': f})
                } for f in obj.fines.all()]
        }