from django.conf import settings


def site_settings(request):
    return {
        "SITE_URL": settings.SITE_URL
    }
