
"""
Get an environment variable name from a page and pull the corresponding value
from the environment.
"""

whiffCategory = "naming"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/envValue - get environment value from computed name
{{/include}}

The <code>whiff_middleware/envValue</code>
gets an entry from the environment using a
computed name.

{{include "example"}}
{{using targetName}}envValue{{/using}}
{{using page}}

{{include "whiff_middleware/envValue"}}
    {{using page}}user_{{get-env REMOTE_ADDR/}}_variable{{/using}}
    {{using default}}no user_{{get-env REMOTE_ADDR/}}_variable value{{/using}}
{{/include}}

{{/using}}
{{/include}}

"""

# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv
from whiff import namecomponent

class envValue(misc.utility):
    def __init__(self,
                 page, # page containing the variable name
                 default=None, # page to deliver if corresponding entry is not found
                 ):
        self.page = page
        self.default = default
    def __call__(self, env, start_response):
        variable = self.param_value(self.page, env)
        if variable:
            variable = variable.strip()
        if not variable:
            raise ValueError, "envValue requires a non-empty variable name"
        (realname, indices) = namecomponent.parse_name(variable)
        if not env.has_key(realname):
            # deliver the default
            if self.default:
                return self.deliver_page(self.default, env, start_response)
            else:
                raise ValueError, "in envValue variable not found in env and no default "+repr(
                    variable)
        # deliver the corresponding env value
        value = env[realname]
        # don't deliver default if indexing is bogus: raise error instead
        for index in indices:
            value = value[index]
        return self.deliver_page(value, env, start_response)

__middleware__ = envValue
