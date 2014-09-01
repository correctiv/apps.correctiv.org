"""
WSGI config for correctiv_apps project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/1.6/howto/deployment/wsgi/
"""

import sys
import os
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "correctiv_apps.settings")

project = os.path.dirname(__file__)
workspace = os.path.join(project, '..')
sys.path.append(project)
sys.path.append(workspace)

from django.core.wsgi import get_wsgi_application
application = get_wsgi_application()

try:
    from dj_static import Cling
    application = Cling(application)
except ImportError:
    pass
