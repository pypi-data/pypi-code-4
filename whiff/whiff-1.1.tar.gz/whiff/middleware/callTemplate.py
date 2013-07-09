
"""
Call a template based on path value argument.

This is useful, for example to allow "login's" which on success
return to any number of possible entry pages.
"""

whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/callTemplate -- expand a page
{{/include}}

The <code>whiff_middleware/CallTemplate</code>
middleware expands a page.
This middleware is sometimes useful for implementing AJAX functionality.
"""

# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv
from whiff import resolver

class callTemplate(misc.utility):
    def __init__(self,
                 path,
                 **arguments
                 ):
        self.path = path
        self.arguments = arguments
    def __call__(self, env, start_response):
        path = self.param_value(self.path, env)
        path = path.strip()
        #pr "RESOLVING", path
        # resolve the path
        root = env.get(whiffenv.ROOT)
        if root is None:
            raise ValueError, "cannot resolve template: no root bound in environment"
        rpath = env.get(whiffenv.TEMPLATE_PATH)
        # resolve relative path
        if rpath and not path.startswith("/"):
            dirpath = rpath[:-1]
            prefix = "/".join(dirpath)
            if prefix:
                path = "/%s/%s" % (prefix, path)
            else:
                path = "/"+path
        args = self.arguments
        #pr "ARGUMENTS", args
        try:
            (application, responding_path, path_remainder) = root.resolve(path, args)
        except resolver.ModuleRootResolutionException:
            raise ValueError, "failed to resolve "+repr(path)
        #pr "NOW CALLING", application
        return application(env, start_response)

__middleware__ = callTemplate

# cannot test this one without complete framework (need whiffenv.ROOT)
