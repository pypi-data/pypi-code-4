
whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/mako/IfMako -- test if Mako templates are available
{{/include}}

The <code>whiff_middleware/IfMako</code>
middleware checks to see whether
<a href="http://www.makotemplates.org/">the Mako templating package [http://www.makotemplates.org/]</a>
has been installed.  If it has been installed it evaluates the <code>page</code> argument as the result
text, or otherwise it evaluates the <code>elsePage</code> argument as the result text.
{{include "example"}}
{{using targetName}}ifMAKO{{/using}}
{{using page}}

{{include "whiff_middleware/mako/IfMako"}}
    {{using page}}
        MAKO IS INSTALLED!
    {{/using}}
    {{using elsePage}}
        MAKO IS NOT INSTALLED!
    {{/using}}
{{/include}}

{{/using}}
{{/include}}

The <code>ifMako</code> middleware is used in this documentation
to allow the documentation application to format web pages even
if the Mako template engine is not installed on the current machine.

"""

from whiff.middleware import misc
from whiff import whiffenv
import types

class IfMako(misc.utility):
    def __init__(self,
                 page,
                 elsePage
                 ):
        self.page = page
        self.elsePage = elsePage
    def __call__(self, env, start_response):
        try:
            from mako.template import Template
        except ImportError:
            return self.deliver_page(self.elsePage, env, start_response)
        return self.deliver_page(self.page, env, start_response)

__middleware__ = IfMako
