from __future__ import absolute_import

class Service(object):
    def initialize(self, request):
        """ Called to initialize the service with an webob.Request.
        
            To keep protocol separation clean, do not try to use the request except to define auth protocols/etc.
        """
        pass


