"""
WHIFF interface for repoze.who.middleware.PluggableAuthenticationMiddleware.
All non-default parameters for the middleware except for the page/application must be installed
as WHIFF resources.
"""


whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/repoze/who - attempt to authenticate user using repoze.who
{{/include}}

The <code>whiff_middleware/repoze/who</code>
middleware is a WHIFF interface for <code>repoze.who.middleware.PluggableAuthenticationMiddleware</code>.
All non-default parameters for the middleware except for the page/application must be installed
as WHIFF resources.
"""



from whiff.middleware import misc
from whiff import gateway
from whiff import whiffenv

class repozeWho(misc.utility):
    def __init__(self, page,
                 identifiersResource=["who.identifiers"],
                 authenticatorsResource=["who.authenticators"],
                 challengersResource=["who.challengers"],
                 mdprovidersResource=["who.mdproviders"],
                 classifierResource=["who.classifier"],
                 challenge_deciderResource=["who.challenge_decider"],
                 log_streamResource=["who.log_stream"],
                 log_levelResource=["who.log_level"],
                 ):
        self.page = page
        self.identifiersResource = identifiersResource
        self.authenticatorsResource = authenticatorsResource
        self.challengersResource = challengersResource
        self.mdprovidersResource = mdprovidersResource
        self.classifierResource = classifierResource
        self.challenge_deciderResource = challenge_deciderResource
        self.log_streamResource = log_streamResource
        self.log_levelResource = log_levelResource
        
    def __call__(self, env, start_response):
        # if repoze.who.identity is already known: don't bother getting the identity again
        # xxx this probably means that you can't have multiple levels of authentication using this mechanism...
        env = env.copy()
        try:
            from repoze.who.middleware import PluggableAuthenticationMiddleware
        except ImportError:
            raise ImportError, "repozeWho WHIFF middleware requires repoze.who installation [http://static.repoze.org/whodocs/]"
        import logging
        from repoze.who.classifiers import default_challenge_decider
        from repoze.who.classifiers import default_request_classifier
        # set the SCRIPT_NAME and the PATH_INFO the way that repoze.who wants them.
        env["SCRIPT_NAME"] = env[whiffenv.APP_PATH]
        env["PATH_INFO"] = env[whiffenv.APP_PATH_INFO]
        #pr; #pr "DUMPING ENV FOR REPOZEWHO"
        #its = env.items()
        #its.sort()
        #for x in its:
            #pr x
        identifiers = self.getResourceFromParam(self.identifiersResource, env)
        authenticators = self.getResourceFromParam(self.authenticatorsResource, env)
        challengers = self.getResourceFromParam(self.challengersResource, env)
        mdproviders = self.getResourceFromParam(self.mdprovidersResource, env, [])
        classifier = self.getResourceFromParam(self.classifierResource, env, default_request_classifier)
        challenge_decider = self.getResourceFromParam(self.challenge_deciderResource, env, default_challenge_decider)
        log_stream = self.getResourceFromParam(self.log_streamResource, env, None)
        log_level = self.getResourceFromParam(self.log_levelResource, env, logging.DEBUG)
        app = ShapeShifter(self.page)
        middleware = PluggableAuthenticationMiddleware(
                app,
                    identifiers,
                    authenticators,
                    challengers,
                    mdproviders,
                    classifier,
                    challenge_decider,
                    log_stream = log_stream,
                    log_level = log_level
                    )
        def who_start_response(status, headers, *whatever):
            "for some reason who calls start response with extra parameters"
            #pr " who_start_response with ", (status, headers, whatever)
            return start_response(status, headers)
        #pr "xxxx calling application"
        result = middleware(env, who_start_response)
        #result = self.page(env, start_response)
        #pr; #pr "xxxx returning result", result
        return result
        
    def getResourceFromParam(self, param, env, defaultValue="forbidden"):
        resourcePath = self.param_json(param, env)
        resource = gateway.getResource(env, resourcePath, defaultValue)
        assert resource!=defaultValue or defaultValue!="forbidden", "repoze.who parameter not found in WHIFF resources (no default)"
        return resource

class ShapeShifter:
    "this is a hack around a repoze.who bug which assumes the start_response is called"
    def __init__(self, app):
        self.app = app
    def __call__(self, env, start_response):
        iterable = iter( self.app(env, start_response) )
        # get the first element to force call to start_response
        first = iterable.next()
        return self.iterate(first, iterable)
    def iterate(self, first, iterable):
        yield first
        for x in iterable:
            yield x

__middleware__ = repozeWho

