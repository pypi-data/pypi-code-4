"""
Middleware to generate an HTML diff between two sources
"""

whiffCategory = "library"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/diff - format a difference display between two texts
{{/include}}

The <code>whiff_middleware/diff</code>
middleware generates an html "diff" display
using the standard Python difflib.  This middleware
requires the <code>whiff_middleware/diff.css</code>
stylesheet.

{{include "example"}}
{{using targetName}}diff{{/using}}
{{using page}}

{{include "whiff_middleware/diff"}}
    {{using fromText}}
#   test:
    example
    text
    before
    change
    edit
    demonstration
    {{/using}}
    {{using toText}}
#   test:
    example
    text
    after
    changing
    edit
    {{/using}}
{{/include}}

{{/using}}
{{/include}}

"""
import difflib

# import must be absolute
from whiff.middleware import misc

class diff(misc.utility):
    def __init__(self,
                 fromText,
                 toText,
                 fromName="old",
                 toName="new",
                 context=False,
                 numlines=20,
                 ):
        self.fromText = fromText
        self.toText = toText
        self.fromName = fromName
        self.toName = toName
        self.context = context
        self.numlines = numlines
    def __call__(self, env, start_response):
        fromText = self.param_value(self.fromText, env)
        toText = self.param_value(self.toText, env)
        fromName = self.param_value(self.fromName, env)
        toName = self.param_value(self.toName, env)
        fromlines = fromText.split("\n")
        tolines = toText.split("\n")
        context = self.param_json(self.context, env)
        numlines = self.param_json(self.numlines, env)
        # could trim unimportant white space...
        outHtmlgenerator = difflib.HtmlDiff().make_table(fromlines, tolines, fromName,
                                                        toName, context, numlines)
        start_response("200 OK", [('Content-Type', 'text/html')])
        return outHtmlgenerator

__middleware__ = diff

def test():
    FROMEXAMPLE = """
def __call__(self, env, start_response):
            parse_cgi = self.param_json(self.parse_cgi, env)
            if parse_cgi:
                cgi = resolver.process_cgi(env, parse_cgi=True)
                json_env = jsonParse.format(env)
                start_response("200 OK", [('Content-Type', 'text/html')])
                app = quoteHtml.__middleware__(json_env)
                return app({}, misc.ignore)                                        
    """

    TOEXAMPLE = """
def __call__(self, env, start_response):
            parse_cgi = self.param_json(self.parse_cgi, env)
            if parse_cgi:
                cgi = resolver.process_cgi(env, parse_cgi=True)
                json_env = jsonParse.format(env)
                start_response("200 OK", [('Content-Type', 'text/plain')])
                app = quoteHtml.__middleware__(json_env)
                return app({}, misc.ignore)                                        
    """
    app = diff(FROMEXAMPLE, TOEXAMPLE)
    print "test output"
    print "".join( app({}, misc.ignore) )

if __name__=="__main__":
    test()
