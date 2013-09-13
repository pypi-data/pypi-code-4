# encoding: utf-8
import logging
from rest_framework.routers import SimpleRouter
from .serializers import OrquestraSerializer
from .api import OrquestraAPI, exception_translation

router = SimpleRouter()
LOG = logging.getLogger(__name__)

__all__ = ['OrquestraSerializer', 'OrquestraAPI', 'exception_translation', 'register']


def register(name, viewsets, *args):
    router.register(name, viewsets, *args)
    LOG.debug(u'Registered api %s with viewset %s', name, viewsets)
