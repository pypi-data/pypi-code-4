
whiffCategory = "logic"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/Noop - no-operation middleware
{{/include}}

The <code>whiff_middleware/Noop</code>
middleware sends its input page as its output
without changing it.
the no-operation middleware is often used as a placeholder
during development and testing.
"""

# import must be absolute
from whiff.middleware import misc

class Noop(misc.utility):
    def __init__(self, page):
        self.page = page
    def __call__(self, env, start_response):
        return list(self.page(env, start_response))

__middleware__ = Noop
