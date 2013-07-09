"""
Middleware to protect an application using repoze.who authentication
by building a "stack" who [ allow [ app ] ].

Also exports as a function (not middleware) protectDirectory.
"""

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/repoze/protect - protect page/application from unauthorized access
{{/include}}
The <code>whiff_middleware/repoze/allow</code> middleware is essentially a combination of <code>who</code> and <code>allow</code>
-- <code>protect</code> attempts to authenticate the user using <code>who</code> and then uses <code>allow</code>
to decide whether the user should be permitted to view the <code>page</code>.
"""

import who
import allow
from whiff import resolver
from whiff.middleware import redirect
from whiff.middleware import absPath
from whiff.middleware import unauthorized

def protect(app, # application to protect
            allowUsers, # users permitted to view the page ("allow" parameter: sequence or None or True)
            failureRedirect=None, # server url to redirect for failures
            **otherWhoArguments):
    """
    Middleware to create an application which allows allowUsers to execute the app,
    redirecting all others to failureRedirect
    """
    if failureRedirect is not None:
        absRedirect = absPath.__middleware__(failureRedirect)
        failurePage = redirect.__middleware__(absRedirect)
    else:
        failurePage = unauthorized.__middleware__("you are not authorized to view this information")
    allowApp = allow.__middleware__(users=allowUsers, page=app, failurePage=failurePage)
    whoApp = who.__middleware__(allowApp, **otherWhoArguments)
    return whoApp

class protectDirectory(resolver.WsgiComponent):
    def __init__(self, module, # the module to protect
                     path, # the url/variable name of the module
                     allowUsers, # users allowed to view the module.
                     failureRedirect, # absolute server path to failure page
                     # the following are the rootModuleApplication arguments except for root_path and root_module
                     on_not_found = None,
                     filter_middleware = None,
                     exception_middleware = None,
                     environment = None,
                     resourceGateway = None,
                     # tack on other who arguments
                     **otherWhoArguments):
        """
        protect a directory in a WHIFF application using repoze.who.
        For example in an __init__.py file:
        import secretsDirectory
        secretsDirectory = protectDirectory(secretsDirectory, "secretsDirectory", ["admin", "gandalf"], "/sorry.html")
        """
        # XXXX this needs to be generalized for user groups...
        self.app = resolver.moduleRootApplication(path, module,
                                         on_not_found=on_not_found,
                                         filter_middleware=filter_middleware,
                                         exception_middleware=exception_middleware,
                                         environment=environment,
                                         resourceGateway=resourceGateway)
        self.args_seq = [module, # the module to protect
                     path, 
                     allowUsers, 
                     failureRedirect, 
                     on_not_found,
                     filter_middleware,
                     exception_middleware,
                     environment,
                     resourceGateway,]
        self.args_dict = otherWhoArguments
        self.whoApp = protect(self.app, allowUsers, failureRedirect, **otherWhoArguments)
    def duplicate(self):
        # duplicate for rebinding  xxxx is this necessary or expensive?
        return protectDirectory(*self.args_seq, **self.args_dict)
    def bind_root(self, root_application, responding_path, path_remainder, outer_arguments):
        # bind the protected underlying root directory
        resolver.WsgiComponent.bind_root(self, root_application, responding_path, path_remainder, outer_arguments)
        self.app.bind_root(root_application, responding_path, path_remainder, outer_arguments)
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        return self.whoApp(env, start_response)

__middleware__ = protect
