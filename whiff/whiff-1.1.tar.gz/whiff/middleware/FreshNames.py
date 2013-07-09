
whiffCategory = "naming"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/FreshNames - create fresh names in environment
{{/include}}

The <code>whiff_middleware/FreshNames</code>
middleware creates a new copy of the WHIFF environment
and introduces entries in that environment whose values
are guaranteed to be "fresh" in the sense that they
have not been used before.  This functionality is useful
to prevent name collisions when generating HTML fragments or
javascript code for example.

{{include "example"}}
{{using targetName}}FreshNames{{/using}}
{{using page}}

{{include "whiff_middleware/FreshNames" names: ["alpha", "beta", "gamma"]}}
    fresh alpha = {{get-id alpha/}} <br>
    fresh beta = {{get-id beta/}} <br>
    fresh gamma = {{get-id gamma/}} <br>
{{/include}}

{{/using}}
{{/include}}
"""

from whiff.middleware import misc
from whiff import gateway
import types

class FreshNames(misc.utility):
    def __init__(self, page):
        self.page = page
    def __call__(self, env, start_response):
        env = env.copy()
        names = env.get("names")
        assert names is not None, "FreshNames requires names environment entry"
        tnames = type(names)
        assert tnames in (types.ListType, types.TupleType), "FreshNames requires name environment entry to be a list or a tuple "+repr(tnames)
        for name in names:
            assert type(name) in types.StringTypes, "FreshNames requires all names to be strings "+repr(name)
            freshValue = gateway.getResource(env, ["freshName", name])
            env[name] = freshValue
        return self.deliver_page(self.page, env, start_response)

__middleware__ = FreshNames
