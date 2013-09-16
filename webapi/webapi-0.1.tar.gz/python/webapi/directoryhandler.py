import webapp2


__author__ = 'nate'


class DirectoryHandler(webapp2.RequestHandler):
    """
        Should return a api directory.
        
        the items should be the various apiinformations in directoryitem form
    """
    def get(self):
        api_infos = self.app.get_apis()
        self.response.write('Show directory of: %s' % api_infos)


class APIDirectory(webapp2.WSGIApplication):
    api_informations = None
    
    def __init__(self, apis, *args, **kwargs):
        super(APIDirectory, self).__init__(*args, **kwargs)
        #self.router.set_dispatcher(self.__class__.custom_dispatcher)
        self.router.add(webapp2.Route('/discovery/v1/apis', DirectoryHandler))
        self.router.add(webapp2.Route('/discovery/v1/apis/<apiname>/<version>/rest', RestDescriptionHandler))
        
        self.api_informations = {}
        self.apis = []
        for api in apis:
            self.api_informations.setdefault(api.name, {})[api.version] = api
            self.apis.append(api) 
            
    def get_apis(self):
        return self.apis
        
    def get_api(self, apiname, version):
        return self.api_informations.get(apiname).get(version)

   #@staticmethod
   #def custom_dispatcher(router, request, response):
   #    rv = router.default_dispatcher(request, response)
   #    if isinstance(rv, basestring):
   #        rv = webapp2.Response(rv)
   #    elif isinstance(rv, tuple):
   #        rv = webapp2.Response(*rv)
#
   #    return rv
#
   #def route(self, *args, **kwargs):
   #    def wrapper(func):
   #        self.router.add(webapp2.Route(handler=func, *args, **kwargs))
   #        return func
#
   #    return wrapper


class RestDescriptionHandler(webapp2.RequestHandler):
    """ should return a discovery document
    
        the response should be the apiinformation encoded as a restdescription
    """
    def get(self, apiname, version):
        api_info = self.app.get_api(apiname, version)
        self.response.write('Show rest desc')