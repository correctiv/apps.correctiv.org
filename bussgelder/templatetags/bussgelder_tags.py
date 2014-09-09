from urllib import urlencode
from urlparse import urlparse, urlsplit, urlunsplit, parse_qs

from django import template
from django.template.defaultfilters import floatformat
from django.contrib.humanize.templatetags.humanize import intcomma

from ..models import GERMAN_STATES_DICT

register = template.Library()


urlencode_utf8 = lambda d: urlencode(
    dict([(k.encode('utf-8'), v.encode('utf-8')) for k, v in d.items()]), True)


def get_state_name(context, key):
    return GERMAN_STATES_DICT.get(key, '')


DECIMAL_SEPARATOR = floatformat(0.0, 2)[1]


def add_embed(url):
    (scheme, netloc, path, query, fragment) = urlsplit(url)
    d = parse_qs(query)
    d = dict([(k, v[0]) for k, v in d.items()])
    d['embed'] = '1'
    query = urlencode_utf8(d)
    return urlunsplit((scheme, netloc, path, query, fragment))


def intcomma_floatformat(value, arg):
    val = intcomma(value)
    if not DECIMAL_SEPARATOR in val:
        val += '%s00' % DECIMAL_SEPARATOR
    else:
        before_comma, after_comma = val.rsplit(DECIMAL_SEPARATOR, 1)
        if len(after_comma) == 0:
            after_comma = '00'
        elif len(after_comma) == 1:
            after_comma += '0'
        val = '%s%s%s' % (before_comma, DECIMAL_SEPARATOR, after_comma)
    return val


def facet_active(context, name, value):
    value = unicode(value)
    request = context['request']
    d = parse_qs(urlparse(request.get_full_path()).query)
    d = dict([(k, v[0]) for k, v in d.items()])
    return d.get(name, '') == value


def facet_vars(context, name, value):
    value = unicode(value)
    request = context['request']
    (scheme, netloc, path, query, fragment) = urlsplit(request.get_full_path())
    d = parse_qs(query)
    d = dict([(k, v[0]) for k, v in d.items()])
    d.pop('page', None)
    if name:
        if not value or d.get(name) == value:
            d.pop(name)
        else:
            d[name] = value

    out = urlencode_utf8(d)
    if name:
        return out
    else:
        context[value] = out
        return ''


register.simple_tag(takes_context=True)(get_state_name)
register.simple_tag(takes_context=True)(facet_vars)
register.assignment_tag(takes_context=True)(facet_active)
register.filter('intcomma_floatformat', intcomma_floatformat)
register.filter('add_embed', add_embed)
