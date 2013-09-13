# encoding: utf-8
import logging
import os.path
from importlib import import_module
from django.conf import settings
from django.conf.urls import patterns, url, include
from django.views.generic.simple import direct_to_template
from application.api import router

LOG = logging.getLogger(__name__)


for app in settings.INSTALLED_APPS:
    if not app.startswith('application.'):
        continue

    try:
        base_module = import_module(app)
        api = import_module("%s.api" % app)
    except ImportError, e:
        if os.path.exists(os.path.abspath(os.path.join(base_module.__file__, '../api.py'))):
            # File exists, error on import
            raise

urlpatterns = patterns(
    'application.api.views',
    url(r'^$', 'api_help', name='api.index'),
    url(r'^', include(router.urls)),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework'))
)
