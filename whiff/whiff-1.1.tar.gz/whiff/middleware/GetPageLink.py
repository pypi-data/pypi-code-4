
whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/GetPageLink - generate a link which
expands into a page template
{{/include}}

The <code>whiff_middleware/getPageLink</code>
middleware "freezes" a page into a URL link which when
followed will expand into the page.  This middleware
is useful, for example, for inlining links to calculated
images.
"""

import urllib

# must be absolute
from whiff.middleware import misc
from whiff.middleware import expandPostedTemplate
from whiff import whiffenv

# XXXX maybe should check for maximum link length sanity check

class GetPageLink(misc.javaScriptGenerator):
    def __init__(self, page, expandRelativeTo=None, expanderUrl="whiff_middleware/getPage", **cgi_arguments):
        self.page = page
        self.expandRelativeTo = expandRelativeTo
        self.expanderUrl = expanderUrl
        self.cgi_arguments = cgi_arguments
    def __call__(self, env, start_response):
        cgi_dictionary = {}
        # don't expand the page -- send text
        pageText = self.param_text(self.page)
        cgi_dictionary["page"] = pageText
        # do expand the "expandRelativeTo" and cgi_arguments
        if self.expandRelativeTo:
            rurl = cgi_dictionary["relativeURL"] = self.param_value(self.expandRelativeTo, env)
            env = expandPostedTemplate.relativeEnvironment(env, rurl)
        elif env.has_key(whiffenv.ENTRY_POINT):
            cgi_dictionary["relativeURL"] = env[whiffenv.ENTRY_POINT]
        for (k,v) in self.cgi_arguments.items():
            cgi_dictionary[k] = self.param_value(v, env)
        query_string = urllib.urlencode(cgi_dictionary)
        expanderUrl = self.param_value(self.expanderUrl, env)
        linkText = "%s?%s" % (expanderUrl, query_string)
        headers = self.derive_headers('text/plain')
        start_response('200 OK', headers)
        return [linkText]

__middleware__ = GetPageLink

def test():
    env = {
        "wsgi.url_scheme" : "http",
        "PATH_INFO" : "/whatever",
        "QUERY_STRING" : "",
        "REMOTE_ADDR" : "127.0.0.1",
        "REMOTE_HOST" : "localhost",
        "REQUEST_METHOD" : "GET",
        "SCRIPT_NAME" : "",
        "SERVER_NAME" : "localhost",
        "SERVER_PORT" : "8888",
        "SERVER_PROTOCOL" : "HTTP/1.1",
        "SERVER_SOFTWARE" : "WSGIServer/0.1 Python/2.5",
        }
    testapp = GetPageLink("test page", otherarg="hi&there")
    print "test link output"
    print "".join(list(testapp(env, misc.ignore)))

if __name__=="__main__":
    test()
