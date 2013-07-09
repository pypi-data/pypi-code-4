"""
	Middleware to automatically catch and display an error traceback using cgitb
        (undocumented method cgitb.html).
"""

whiffCategory = "logic"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/simpleTraceback - convert exception to text/plain traceback
{{/include}}

The <code>whiff_middleware/simpleTraceback</code>
middleware catches any exception raised by a page
and renders an HTML traceback for the exception.

{{include "example"}}
{{using targetName}}simpleTraceback{{/using}}
{{using page}}

{{include "whiff_middleware/simpleTraceback"}}
     {{get-env "noSuchEnvironmentEntry"/}}
{{/include}}

{{/using}}
{{/include}}

"""

#import cgitb
import traceback
import sys
from whiff import resolver

# if verbose is True then information is dumped to stdout
# (which breaks cgi scripts and old mod-wsgi installations).
VERBOSE = False

class displayTraceback:
    def __init__(self, page, verbose=VERBOSE):
        self.verbose = verbose
        self.page = page
    def __call__(self, env, start_response):
        page = self.page
        start_response = callOnce(start_response)
        #pr "displayTraceback called for", page
        try:
            pageContentSequence = page(env, start_response)
            pageContentList = list(pageContentSequence)
            return pageContentList
        except:
            info = sys.exc_info()
            if self.verbose:
                print "verbose: display traceback caught exception for", page
            diagnosticOutput = traceback.format_exc(1000) # cgitb.html(info)
            start_response('200 OK', [('Content-Type', 'text/plain'),])
            if self.verbose:
                print "verbose traceback"
                (a,b,tb) = info
                traceback.print_tb(tb) # verbose
                print a # verbose
                print b # verbose
            return [diagnosticOutput]

class callOnce:
    def __init__(self, fn):
        self.fn = fn
        self.called = False
    def __call__(self, *args):
        if self.called:
            return # ignore any but the first call
        fn = self.fn
        self.called = True
        return fn(*args)

__middleware__ = displayTraceback
