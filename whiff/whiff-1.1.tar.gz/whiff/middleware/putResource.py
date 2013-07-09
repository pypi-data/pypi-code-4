
"""
Install a resource value by path
"""

whiffCategory = "naming"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/putResource - install a resource value by path
{{/include}}

The <code>whiff_middleware/putResource</code>
middleware attempts to install a resource value at a path.
As a security precaution, templates which are tainted by
a remote submission are not allowed to directly execute
this middleware.
{{include "example"}}
{{using targetName}}putResource{{/using}}
{{using page}}

{{include "whiff_middleware/putResource"}}
    {{using path}} ["local", "MAGIC_VARIABLE"] {{/using}}
    {{using value}} MY SPECIAL MAGIC VALUE {{/using}}
{{/include}}

The magic text value is:
{{include "whiff_middleware/getResource"}}
     ["local", "MAGIC_VARIABLE"] 
{{/include}}

{{/using}}
{{/include}}

"""
import types

# import must be absolute
from whiff.middleware import misc
from whiff import gateway
from whiff import whiffenv

class putResource(misc.utility):
    def __init__(self,
                 value, # the resource path list as json
                 path, # the new value for the resource
                 as_json=False,
                 ):
        self.path = path
        self.value = value
        self.as_json = as_json
    def __call__(self, env, start_response):
        resourcePathList = self.param_json(self.path, env)
        # disallow "puts" to all resources except "local"
        if len(resourcePathList)>0 and resourcePathList[0]!="local":
            assert not whiffenv.rpc_tainted(env), "security violation: can't put non-local resource from tainted environment "+repr(resourcePathList)
        as_json = self.param_json(self.as_json, env)
        #resource_value = root.getResource(resourcePathList)
        if as_json:
            new_value = self.param_json(self.value, env)
        else:
            new_value = self.param_value(self.value, env)
        gateway.putResource(env, resourcePathList, new_value)
        # deliver an empty page
        return self.deliver_page("", env, start_response)

__middleware__ = putResource
