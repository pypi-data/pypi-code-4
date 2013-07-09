"""
Interpret page as a relative path relative to the calling
template and return the equivalent absolute HTTP path.
"""

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/absPath - find absolute HTTP path
{{/include}}

The <code>whiff_middleware/absPath</code>
middleware translates a server-relative URL path to a
server-absolute URL path positioned relative
to the current WHIFF component.

{{include "example"}}
{{using targetName}}absPath{{/using}}
{{using page}}

absolute HTTP path for relative/path is
{{include "whiff_middleware/absPath"}}relative/path{{/include}}

{{/using}}
{{/include}}

"""

whiffCategory = "formatting"

# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv

class absPath(misc.utility):
    def __init__(self,
                 page):
        self.page = page
    def __call__(self, env, start_response):
        relativePath = self.param_value(self.page, env)
        relativePath = relativePath.strip()
        #pr "absPath unrelativizing", repr(relativePath)
        root = env[whiffenv.ROOT]
        template_path = env.get(whiffenv.TEMPLATE_PATH)
        result = root.absolute_path(relativePath, template_path, clean=False)
        #pr "absPath got", repr(result)
        return self.deliver_page(result, env, start_response)

__middleware__ = absPath
