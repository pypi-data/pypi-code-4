"""
Create a page from an URL encoding which was encoded by pageToUrl.
"""

whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/urlToPage - convert URL to page
{{/include}}

The <code>whiff_middleware/urlToPage</code>
middleware converts a URL to a page.  This is the
inverse operation of <code>pageToUrl</code>.

"""

from whiff.middleware import misc
from whiff import resolver
from whiff import whiffenv
from whiff.rdjson import jsonParse

class urlToPage(misc.utility):
    def __init__(self):
        pass
    def __call__(self, env, start_response):
        env = resolver.process_cgi(env, parse_cgi=True)
        qcontent = whiffenv.cgiGet(env, "content")
        qjheaders = whiffenv.cgiGet(env, "headers")
        qstatus = whiffenv.cgiGet(env, "status")
        content = resolver.unquote(qcontent)
        status = str(resolver.unquote(qstatus))
        jheaders = resolver.unquote(qjheaders)
        (flag,headers,cursor) = jsonParse.parseValue(jheaders)
        #pr"starting response", (status, headers)
        #status = "200 OK"
        headers = [(str(h), str(v)) for (h,v) in headers]
        #headers = [('Content-type', 'text/html')]
        #content = "whatever"
        start_response(status, headers)
        #pr"sending content", [content]
        return [content]

__middleware__ = urlToPage
