from django.conf.urls import patterns, url

from .views import FineSearchView, OrganisationDetail


urlpatterns = patterns('',
    url(r'^$',
        FineSearchView.as_view(),
        name='bussgelder_search'),
    url(r'^empfaenger/(?P<slug>[\w-]+)/$',
        OrganisationDetail.as_view(),
        name='bussgelder_organisation_detail'),
)
