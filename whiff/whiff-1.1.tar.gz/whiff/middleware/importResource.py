
"""
map a resource value into the environment
"""

whiffCategory = "naming"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/importResource - put resource value in environment
{{/include}}

The <code>whiff_middleware/importResource</code>
middleware maps a resource value into an environment entry.
This is especially useful for generating temporary variable
names used in multiple places in javascript code fragments.

{{include "example"}}
{{using targetName}}importResources{{/using}}
{{using page}}

{{include "whiff_middleware/importResource"}}
    {{using name}}VARIABLE_NAME{{/using}}
    {{using path}} ["freshName", "testName"] {{/using}}
    {{using page}}
        The imported value is {{get-env VARIABLE_NAME/}}
    {{/using}}
{{/include}}

{{/using}}
{{/include}}

"""


import types

# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv
from whiff import gateway

class importResource(misc.utility):
    def __init__(self,
                 page, # the page to use the resource
                 name, # the name to assign to the resource
                 path, # the path to the resource
                 ):
        self.page = page
        self.name = name
        self.path = path
    def __call__(self, env, start_response):
        assert not whiffenv.rpc_tainted(env), "security violation: can't import resource from tainted environment"
        resourcePathList = self.param_json(self.path, env)
        #root = env.get(whiffenv.ROOT)
        ##pr "root is", root
        #if root is None:
        #    raise ValueError, "cannot find root resolver in environment"
        #resource_value = root.getResource(resourcePathList)
        resource_value = gateway.getResource(env, resourcePathList)
        env = env.copy()
        name = self.param_value(self.name, env).strip()
        env[name] = resource_value
        return self.deliver_page(self.page, env, start_response)

__middleware__ = importResource
