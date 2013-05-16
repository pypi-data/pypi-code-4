from logging import getLogger
try:
    from cProfile import Profile
except ImportError:
    from Profile import Profile

from django.conf import settings

from dprofiling.backends import get_backend
from dprofiling.models import Session



log = getLogger('dprofiling.middleware')

class ProfilingRequestMiddleware(object):
    def __init__(self, backend=get_backend(), *args, **kwags):
        self.backend = backend

    def enabled(self, request):
        if hasattr(request, '_profiling_enabled'):
            return request._profiling_enabled

        count = Session.on_site.filter(path=request.path, active=True).count()

        request._profiling_enabled = False
        if count == 1:
            request._profiling_enabled = True
        elif count > 1:
            log.error('Multiple profile stats active for the requested url')
        return request._profiling_enabled

    def process_request(self, request):
        if self.enabled(request):
            log.debug('Enabling profiling on %s' % (request.path,))
            request._profile = Profile()
            request._profile.enable()
        return None

    def process_response(self, request, response):
        if self.enabled(request):
            request._profile.disable()
            log.debug('Finished profiling of %s' % (request.path,))
            self.backend.store(request.path, request._profile)
            log.debug('Profile information stored for %s' % (request.path,))
            response.profile = request._profile
            log.debug('Profile information added to the response')

        return response

