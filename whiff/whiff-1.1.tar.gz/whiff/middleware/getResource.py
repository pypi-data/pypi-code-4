
"""
Return a resource value
"""

whiffCategory = "naming"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/getResource - get a resource value
{{/include}}

The <code>whiff_middleware/getResource</code>
middleware gets a value associated with a resource path.
As a security precaution requests which are tainted as
a posted template are not allowed to directly use this
middleware.

{{include "example"}}
{{using targetName}}getResource{{/using}}
{{using page}}

{{include "whiff_middleware/getResource"}} ["freshName", "dummyName"] {{/include}}

{{/using}}
{{/include}}

"""

import types

# import must be absolute
from whiff.middleware import misc
from whiff import gateway
from whiff import whiffenv
from whiff import stream

class getResource(misc.utility):
    def __init__(self,
                 page, # the resource path list as json
                 as_json=False,
                 ):
        self.page = page
        self.as_json = as_json
    def __call__(self, env, start_response):
        resourcePathList = self.param_json(self.page, env)
        # prevent tainted access to non-local resources
        if resourcePathList and resourcePathList[0]!="local":
            assert not whiffenv.rpc_tainted(env), "security violation: can't get resource from tainted environment"
        as_json = self.param_json(self.as_json, env)
        resource_value = gateway.getResource(env, resourcePathList)
        if as_json or type(resource_value) in whiffenv.JSON_TYPES:
            return self.deliver_json(resource_value, env, start_response)
        else:
            return self.deliver_page(resource_value, env, start_response)

__middleware__ = getResource
