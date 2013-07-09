
"""
Get an form variable name from a page and pull the corresponding value
from the environment.
"""

whiffCategory = "naming"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/cgiValue - get a form value using a computed name
{{/include}}

The <code>whiff_middleware/cgiValue</code>
middleware is a dynamic variant of the <code>get-cgi</code>
directive.
This middleware can be useful for manipulating forms which
do not have a fixed number of input parameters.

{{include "example"}}
{{using targetName}}cgiValue{{/using}}
{{using page}}

{{include "whiff_middleware/cgiValue"}}
    {{using page}}user_{{get-env REMOTE_ADDR/}}_password{{/using}}
    {{using default}}NO PASSWORD AVAILABLE FOR {{get-env REMOTE_ADDR/}} user{{/using}}
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
        value = whiffenv.cgiGet(env, variable)
        if value is None:
            # deliver the default
            if self.default:
                return self.deliver_page(self.default, env, start_response)
            else:
                raise ValueError, "in cgiValue variable not found in cgi dict and no default "+repr(
                    variable)
        # deliver the corresponding cgi value
        return self.deliver_page(value, env, start_response)

__middleware__ = envValue
