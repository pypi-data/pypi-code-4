"""
Interpret page as a relative path relative to the
calling template and return the equivalent file system path.
"""

whiffCategory = "naming"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/filePath - find absolute file system path
{{/include}}

The <code>whiff_middleware/filePath</code>
middleware translates a server-relative URL path to a
file system absolute path positioned relative
to the current WHIFF component.  For security reasons
templates tainted by remote evaluation may not
execute this middleware directly.

{{include "example"}}
{{using targetName}}filePath{{/using}}
{{using page}}

absolute file system path for ../relative/path is
{{include "whiff_middleware/filePath"}}../relative/path{{/include}}

{{/using}}
{{/include}}

"""


# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv
import os

class filePath(misc.utility):
    def __init__(self,
                 page):
        self.page = page
    def __call__(self, env, start_response):
        assert not whiffenv.rpc_tainted(env), "security violation: cannot compute file system path from rpc tainted environment"
        relativePath = self.param_value(self.page, env)
        relativePath = relativePath.strip()
        #pr "absPath unrelativizing", repr(relativePath)
        source_path = env[whiffenv.SOURCE_PATH]
        template_path = env.get(whiffenv.SOURCE_PATH)
        (directory, filename) = os.path.split(template_path)
        unclean_path = os.path.join(directory, relativePath)
        result = os.path.abspath(unclean_path)
        #pr "absPath got", repr(result)
        return self.deliver_page(result, env, start_response)

__middleware__ = filePath
