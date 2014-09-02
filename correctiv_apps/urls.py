from django.conf.urls import patterns, include, url
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

admin.autodiscover()


urlpatterns = patterns('',
    url(r'^justizgelder/', include('bussgelder.urls', namespace='bussgelder')),
    (r'^tinymce/', include('tinymce.urls')),
    url(r'^admin/', include(admin.site.urls)),
)


if settings.DEBUG:
    urlpatterns += staticfiles_urlpatterns()
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


def handler500(request):
    """
    500 error handler which includes ``request`` in the context.
    """

    from django.shortcuts import render
    return render(request, '500.html', {'request': request}, status=500)
