
whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/jquery/jQueryUIBase - jquery support
{{/include}}

The <code>jQueryUIBase</code> middleware provides support for generating
javascript fragments frequently useful for using the <code>jquery</code>
javascript library -- please see the <code>whiff/jquery</code> tutorial for more information.
the <code>jQueryUIBase</code> middleware is suitable for inclusion directly in an
HTML document.  It automatically includes supporting libraries if needed.
"""


from whiff.middleware import misc
from whiff.middleware import callTemplate
import jQueryUIBaseJs

class jQueryUI(misc.utility):
    def __init__(self,
                 targetId,
                 widget,
                 **other_parameters):
        self.targetId = targetId
        self.widget = widget
        self.other_parameters = other_parameters
    def __call__(self, env, start_response):
        #targetId = self.param_value(self.targetId, env).strip()
        #widget = self.param_value(self.widget, env).strip()
        # generate javascript includes if needed
        libsApplication = callTemplate.callTemplate("whiff_middleware/jquery/jQueryUILib")
        libs = self.param_value(libsApplication, env)
        jsApp = jQueryUIBaseJs.__middleware__(self.targetId, self.widget, **self.other_parameters)
        jsText = self.param_value(jsApp, env)
        # yield response
        start_response('200 OK', [('Content-Type', 'text/html')])
        # include the javascript libraries if needed
        yield libs
        # generate javascript
        yield '<script type="text/javascript">\n'
        yield jsText
        yield '</script>\n'

__middleware__ = jQueryUI
