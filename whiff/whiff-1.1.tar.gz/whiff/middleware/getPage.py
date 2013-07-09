"""
Interpret a cgi request as a template expansion.
"""

whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/getPage - expand CGI request as a template
{{/include}}

The <code>whiff_middleware/getPage</code>
middleware interpret a cgi request as a template expansion.
This is useful, for example, to interpret image links as template expansions.
The template to expand is provided as the required cgi variable "page".
The relative URL for expansion is provided as the optional
cgi variable "relativeURL".
Other cgi parameters are passed through to the page.
"""

import types
from whiff import parseTemplate
from whiff import resolver
from whiff import whiffenv
from whiff.rdjson import jsonParse

# import must be absolute
from whiff.middleware import expandPostedTemplate

VERBOSE = False

class getPage(resolver.WsgiComponent):
    def __init__(self):
        # no initialization needed?
        pass
    def duplicate(self):
        return getPage()
    def whiff_call(self, env, start_response,
                   update_environment=None, additional_args=None):
        # parse the input
        #pr
        #pr "getPage whiff_call"
        # get cgi parameters
        if update_environment:
            env = update_environment(env)
        env = resolver.process_cgi(env, parse_get=True)
        cgi_dict = env[whiffenv.CGI_DICTIONARY]
        pages = cgi_dict.get("page")
        if not pages:
            raise ValueError, "required page require missing"
        if len(pages)>1:
            raise ValueError, "too many page parameters"
        templateText = pages[0]
        relativeUrl = None # default
        urls = cgi_dict.get("relativeURL")
        if urls and len(urls)==1:
            relativeUrl = urls[0]
        templateText = resolver.unquote(templateText)
        if VERBOSE:
            print "verbose: GOT RELATIVE URL", relativeUrl
            print ; print "verbose: TEMPLATE TEXT"
            print templateText # verbose
            print "verbose: END OF TEMPLATE TEXT"
        # create the template
        (test, result, cursor) = parseTemplate.parse_page(templateText)
        if not test:
            c1 = templateText[ max(0, cursor-20): cursor ]
            c2 = templateText[ cursor : cursor+20 ]
            raise ValueError, "template parse for payload reports error "+repr((result, cursor, c1, c2))
        page = result
        # get stream from page
        stream = page.makeWsgiComponent()
        # by default, bind the stream same as self
        #stream.bind_root(self.whiff_root_application, self.whiff_responding_path,
        #                 self.whiff_path_remainder, self.whiff_outer_arguments)
        root_application = self.whiff_root_application
        responding_path = self.whiff_responding_path
        path_remainder = self.whiff_path_remainder
        outer_arguments = self.whiff_outer_arguments
        if relativeUrl is not None:
            env = expandPostedTemplate.relativeEnvironment(env, relativeUrl)
            responding_path = relativeUrl.split("/")
            path_remainder = []
        stream.bind_root(root_application, responding_path, path_remainder, outer_arguments)
        #pr "binding url at", (responding_path, path_remainder)
        # evaluate the template
        result = stream(env, start_response)
        #pr "EXPANDED RESULT DUMP"
        result = list(result) # FOR DEBUG
        #for x in result: # FOR DEBUG
            #pr x # FOR DEBUG
        #pr "END OF EXPANDED RESULT DUMP"
        # return the text generated
        return result

__wsgi__ = getPage()
