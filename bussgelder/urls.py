from django.conf.urls import patterns, url

from .views import OrganisationSearchView, OrganisationDetail


urlpatterns = patterns('',
    url(r'^$',
        OrganisationSearchView.as_view(),
        name='search'),
    url(r'^empfaenger/(?P<slug>[\w-]+)/$',
        OrganisationDetail.as_view(),
        name='organisation_detail'),
)
