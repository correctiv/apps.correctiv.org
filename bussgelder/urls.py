from django.conf.urls import patterns, url

from .views import OrganisationDetail


urlpatterns = patterns('',
    url(r'^$', 'bussgelder.views.search', name='haystack_search'),
    url(r'^empfaenger/(?P<slug>[\w-]+)/$', OrganisationDetail.as_view(), name='bussgelder_organisation_detail'),
)
