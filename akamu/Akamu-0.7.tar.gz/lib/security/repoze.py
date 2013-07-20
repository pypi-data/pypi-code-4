from akamu.wheezy import WheezyCachingAdapterSetup
from akara import global_config, request, module_config, response

class requires_authority(object):
    """

    Used with WheezyRepozeWrapper and RepozeWrapper as innermost decorator of
    akara service to indicate that authentication is required and cause
    401 response if there is none.  The first argument is the
    message to send to the client

    @requires_authority('Not authorized')
    def akara_service(): pass

    """
    def __init__(self, message = 'Not authorized', noauth = False):
        self.message = message
        self.noauth  = noauth
    def __call__(self, func):
        def innerHandler(*args, **kwds):
            if 'REMOTE_USER' not in request.environ and not self.noauth:
                response.code = 401
                return self.message
            else:
                if '_' in kwds:
                    del kwds['_']
                return func(*args, **kwds)
        return innerHandler