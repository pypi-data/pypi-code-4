
whiffCategory = "library"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/pygmentsCss - provide CSS class definitions
{{/include}}

The <code>whiff_middleware/absPath</code>
middleware 
generates a Pygments CSS style definition sequence.
The optional <code>cssClassName</code> argument
allows definition of a non-default css class name.
"""

from pygments.formatters import HtmlFormatter # this middleware requires Pygments!

# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv
from whiff import resolver

# environment key which may name the css class
envCssClassName = "pygmentsCss.cssClass"

# default css class
defaultCssClassName = "highlight"

class pygmentsCss(misc.utility):
    def __init__(self, cssClass=None):
        self.cssClass = cssClass
    def __call__(self, env, start_response):
        cssClassName = None
        if self.cssClass:
            cssClassName = self.param_value(self.cssClass, env) 
        else:
            # check for environment entry
            cssClassName = env.get(envCssClassName)
        if cssClassName is None:
            cssClassName = defaultCssClassName
        cssClassName = cssClassName.strip()
        payload = HtmlFormatter().get_style_defs("."+cssClassName)
        start_response("200 OK", [('Content-Type', 'text/css')])
        return [payload]
    
__middleware__ = pygmentsCss

def test():
    app = pygmentsCss("className")
    print "test output", app({}, misc.ignore)

if __name__=="__main__":
    test()
