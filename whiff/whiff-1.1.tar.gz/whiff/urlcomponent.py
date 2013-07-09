
import argcomponent
import whiffenv

class UrlComponent(argcomponent.Invocation):
    "url component for inclusion in streams"
    # FOR SECURITY THIS SHOULD NEVER SUPPORT REMOTE URLS (OUTSIDE OF SERVER) (?)
    tag_name = "include"
    def dumpId(self):
        return repr(self.argId)
    def get_arg(self, env, additional_args=None):
        # modify the environment to emulate a direct call to url
        #env = self.update_environment(env) # DON'T DUPLICATE CALL TO UPDATE_ENVIRONMENT
        url = self.argId
        url = resolveUrl(url, self.responding_path)
        env = urlEnv(env, url)
        root_application = self.root_application
        args = self.boundArguments
        #pr "BOUND ARGS FOR URL", url, "ARE", args
        if args is None:
            raise ValueError, "attempt to evaluate unbound url component"
        #pr  "NOW RESOLVING URL", (url, args)
        #pr  "   in", root_application
        (resolution, responding_path, path_remainder) = root_application.resolve(url, args, env=env)
        env[whiffenv.RESPONDING_PATH] = responding_path
        env[whiffenv.PATH_REMAINDER] = path_remainder
        #pr "   SET resolution to (res, rp, pr)", (resolution, responding_path, path_remainder)
        return (resolution, env)

def urlEnv(env, url):
    env = env.copy()
    #pr "urlEnv: replacing script name and path info", (env.get("SCRIPT_NAME"), env.get("PATH_INFO"))
    env["SCRIPT_NAME"] = url
    env["PATH_INFO"] = ""
    #pr "urlEnv: replaced script name and path info", (env.get("SCRIPT_NAME"), env.get("PATH_INFO"))
    return env

def resolveUrl(url, responding_path):
    if url.startswith("/"):
        #return url
        pass
    else:
        # relative path
        url = "/"+url
        if responding_path:
            directory_path = responding_path[:-1]
        else:
            directory_path = []
        prefix = "/".join(directory_path)
        if prefix:
            url = "/%s%s" % (prefix, url)
        #return url
    while url.startswith("//"):
        url = url[1:]
    return url

import resolver

class UrlResolver(resolver.WsgiComponent):
    def __init__(self, url, args):
        self.url = url
        self.args = args
        #pr "url resolver created", (self.url, self.args.keys())
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        responding_path = None
        url = self.url
        responding_path = self.whiff_responding_path
        url = resolveUrl(url, responding_path)
        #if True or update_environment:
        #else:
        #    pass
        env = urlEnv(env, url)
        root_application = self.whiff_root_application
        args = self.args
        #pr "url resolver resolving", (url, args)
        (resolution, responding_path, path_remainder) = root_application.resolve(url, args)
        return resolution(env, start_response, update_environment)

class UrlBinding(resolver.WsgiComponentFactory):
    def __init__(self, url):
        self.url = url
    def clone(self):
        return UrlBinding(self.url)
    def makeWsgiComponent(self, **args):
        url = self.url
        return UrlResolver(url, args)
        
    

        
