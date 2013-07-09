
"""
Install an environment entry by computed name
"""

whiffCategory = "naming"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/putEnvironment - install an environment entry with a computed name
{{/include}}

The <code>whiff_middleware/putEnvironment</code>
middleware attempts to install an environment entry using a computed name.
As a security precaution, templates which are tainted by
a remote submission are not allowed to directly set 
whiff environment directives.
{{include "example"}}

{{using targetName}}putEnvironment{{/using}}
{{using page}}

{{include "whiff_middleware/putEnvironment"}}
    {{using name}}user_{{get-env REMOTE_ADDR/}}_variable{{/using}}
    {{using value}} MY SPECIAL MAGIC VALUE {{/using}}
    {{using page}}

	The user_{{get-env REMOTE_ADDR/}}_variable value is:

	{{include "whiff_middleware/envValue"}}
	    {{using page}}user_{{get-env REMOTE_ADDR/}}_variable{{/using}}
	    {{using default}}no user_{{get-env REMOTE_ADDR/}}_variable value{{/using}}
	{{/include}}

    {{/using}}
{{/include}}

{{/using}}
{{/include}}

"""
import types

# import must be absolute
from whiff.middleware import misc
from whiff import gateway
from whiff import whiffenv

class putEnvironment(misc.utility):
    def __init__(self,
                 value,
                 name,
                 page,
                 as_json=False,
                 ):
        self.name = name
        self.value = value
        self.page = page
        self.as_json = as_json
    def __call__(self, env, start_response):
        name = self.param_value(self.name, env)
        if name.startswith("whiff"):
            assert not whiffenv.rpc_tainted(env), "security: computed env whiff.* names disallowed for rpc's"
        as_json = self.param_json(self.as_json, env)
        if as_json:
            new_value = self.param_json(self.value, env)
        else:
            new_value = self.param_value(self.value, env)
        #pr "now setting", (name, new_value)
        env[name] = new_value
        # deliver an empty page
        return self.deliver_page(self.page, env, start_response)

__middleware__ = putEnvironment
