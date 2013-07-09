"""
Apply middleware only if page returns html, otherwise just return page content.

Note that this middleware will always "evaluate" the page even if the inner middleware doesn't use/need it.
"""

whiffCategory = "logic"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/wrapIfHtml - apply wrapper only to HTML content
{{/include}}

The <code>whiff_middleware/wrapIfHtml</code>
middleware applies a middleware to the page only if the page
generates HTML content.  This is useful, for example to provide
standard headers and footers to all applications under a root directory
that produce HTML, without damaging any PDF or binary image content
produced by applications in that directory.

"""

from whiff.middleware import misc
from wsgiref.headers import Headers

class wrapIfHtml:
    def __init__(self, middleware, page, wrap_mime_type="text/html"):
        #pr "wrapIfHtml", (middleware, page, wrap_mime_type)
        self.wrap_mime_type = wrap_mime_type
        self.page = page
        self.middleware = middleware
        self.headers_recieved = None
        self.status_recieved = None
        self.content_type = None
        self.external_start_response = None
    def my_start_response(self, status, headers):
        self.status_recieved = status
        self.headers_recieved = headers
        for (name, value) in headers:
            #pr "checking", (name, value)
            if name.lower()=="content-type":
                #pr "found"
                self.content_type = value
        if not self.content_type:
            raise ValueError, "no content-type found "+repr(headers)
        #pr "my_start_response found content_type", self.content_type
    def __call__(self, env, start_response):
        page = self.page
        self.external_start_response = start_response
        pageContentSequence = page(env, self.my_start_response)
        # convert to list to force call to start_response
        #pageContentList = list(pageContentSequence)
        pageContentGenerator = misc.regenerate(pageContentSequence)
        content_type = self.content_type
        if content_type is None:
            raise ValueError, "start_response not called by page"
        if content_type==self.wrap_mime_type:
            middleware = self.middleware
            #pr "content-type matches: wrapping", (content_type, self.wrap_mime_type, middleware)
            # wrap the page (emulated) with the middleware...
            fakePage = pageEmulation(self.status_recieved, self.headers_recieved, list(pageContentGenerator))
            wrappedpage = middleware(fakePage)
            return wrappedpage(env, start_response)
        # otherwise just return the page content
        #pr "content-type doesn't match return", content_type
        start_response(self.status_recieved, self.headers_recieved)
        return pageContentGenerator

class pageEmulation:
    def __init__(self, status, headers, contentseq):
        self.status = status
        self.headers = headers
        self.contentseq = contentseq
    def __call__(self, env, start_response):
        #pr "starting with header", self.headers
        start_response(self.status, self.headers)
        return self.contentseq

__middleware__ = wrapIfHtml
