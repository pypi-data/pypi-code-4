"""
Read a json stream from request a form
[   [parameter, value],
    [parameter, value],
    ...
    templatechunk,
    templatechunk,
    ...
    relativeUrl]
Create the template from the chunks.
Insert the cgi parameters and values.
Return result of executing the template as http response.
"""

whiffCategory = "ajax"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/expandPostedTemplate - process server callback
{{/include}}

The <code>whiff_middleware/expandPostedTemplate</code>
middleware is useful for implementing AJAX-type
functionality.  It accepts a "server callback" of form
{{include "javascript"}}
[   [parameter, value],
    [parameter, value],
    ...
    templatechunk,
    templatechunk,
    ...
    relativeUrl]
{{/include}}
Create the template from the chunks.
Insert the cgi parameters and values.
Return result of executing the template as http response.
"""

import sys
import types
from whiff import parseTemplate
from whiff import resolver
from whiff import whiffenv
from whiff.rdjson import jsonParse

VERBOSE = False

class expandPostedTemplate(resolver.WsgiComponent):
    def __init__(self):
        # no initialization needed?
        pass
    def duplicate(self):
        return expandPostedTemplate()
    def whiff_call(self, env, start_response, update_environment=None, additional_args=None):
        if update_environment: env = update_environment(env)
        # parse the input
        #pr
        #pr >> sys.stderr, "expandPostedTemplate whiff_call"
        content_length = None
        content_length_str = env.get("CONTENT_LENGTH")
        if not content_length_str:
            #raise ValueError, "no post content length found"
            pass
        else:
            content_length = int(content_length_str)
        inputFile = env.get("wsgi.input")
        if not inputFile:
            raise ValueError, "no wsgi.input found"
        if content_length is None:
            data = inputFile.read()
        else:
            data = inputFile.read(content_length)
        verbose = VERBOSE or env.has_key("expandPostedTemplate.verbose")
        if verbose:
            print >> sys.stderr,""; print >> sys.stderr," verbose EXPAND TEMPLATE REQUEST DATA"
            print >> sys.stderr,data # verbose
            print >> sys.stderr,"verbose END OF DATA"
        (test, json, cursor) = jsonParse.parseValue(data)
        if not test:
            c1 = data[ max(0, cursor-20) : cursor ]
            c2 = data[ cursor : cursor+20 ]
            raise ValueError, "json parse reports error "+repr((json, cursor, c1, c2))
        if type(json)!=types.TupleType:
            raise ValueError, "expect json payload with tuple, got "+repr(type(json))
        # decompose the parsed json payload:
        # first get the parameters
        parameters = []
        i = 0
        lenjson = len(json)
        while i<lenjson:
            pair = json[i]
            #pr "found pair", repr(pair)
            if type(pair)!=types.TupleType:
                break # end of parameters
            [k,v] = pair
            k = str(k)
            parameters.append( (k,v) )
            i += 1
        # ...then get the template in chunks
        templatechunks = json[i:-2]
        templateText = "".join(templatechunks)
        # tail is prefix followed by relative URL (might be None)
        (cgi_prefix, relativeUrl) = json[-2:]
        if verbose:
            print >> sys.stderr,"verbose: GOT RELATIVE URL", relativeUrl
            print >> sys.stderr,"verbose: GOT CGI_PREFIX", cgi_prefix
            print >> sys.stderr,""; print >> sys.stderr,"verbose: TEMPLATE TEXT"
            print >> sys.stderr,templateText # verbose
            print >> sys.stderr,"verbose: END OF TEMPLATE TEXT"
        # create the template
        (test, result, cursor) = parseTemplate.parse_page(templateText, file_path="[posted template: %s...]"% repr(templateText.strip()[:80]))
        if not test:
            c1 = templateText[ max(0, cursor-20): cursor ]
            c2 = templateText[ cursor : cursor+20 ]
            if verbose: print >> sys.stderr,"template parse error"
            raise ValueError, "template parse for payload reports error "+repr((result, cursor, c1, c2))
        page = result
        # inject the cgi parameters into the page as defaults... (make sure the prefix is observed if present)
        #for (k,v) in parameters:
        #    #pr "injecting default cgi", (k,v)
        #    page.add_cgi_default(k,v)
        # get stream from page
        if verbose: print >> sys.stderr,"made wsgi component"
        stream = page.makeWsgiComponent()
        # by default, bind the stream same as self
        #stream.bind_root(self.whiff_root_application, self.whiff_responding_path,
        #                 self.whiff_path_remainder, self.whiff_outer_arguments)
        root_application = self.whiff_root_application
        responding_path = self.whiff_responding_path
        path_remainder = self.whiff_path_remainder
        outer_arguments = self.whiff_outer_arguments
        # fake cgi-parsing
        resolver.find_or_make_cgi_dictionary(env)
        # if the relative URL is provided, adjust the environment, and stream binding
        if relativeUrl is not None:
            env = relativeEnvironment(env, relativeUrl)
            if verbose: print >> sys.stderr, "splitting", relativeUrl
            responding_path = relativeUrl.split("/")
            path_remainder = []
        if cgi_prefix is not None:
            env[whiffenv.FULL_CGI_PREFIX] = cgi_prefix
        if verbose: print >> sys.stderr,"binding root"
        stream.bind_root(root_application, responding_path, path_remainder, outer_arguments)
        if verbose: print >> sys.stderr,"binding url at", (responding_path, path_remainder)
        # as a security precaution mark the environment as tainted
        env = whiffenv.mark_rpc_tainted(env)
        # inject the cgi parameters QUOTED VALUES!
        for (k,v) in parameters:
            #v = resolver.quote(v) # override_cgi_require automatically does quoting
            if verbose: print >> sys.stderr,"overriding cgi argument", (k,v)
            resolver.override_cgi_require(env, k, v)
        # evaluate the template
        if verbose: print >> sys.stderr,"now evaluating stream"
        try:
            result = stream(env, start_response)
        except:
            if verbose: print >> sys.stderr,"failed to evaluate stream", sys.exc_type, sys.exc_value
            raise
        #pr "EXPANDED RESULT DUMP"
        try:
            result = list(result) # FOR DEBUG
        except:
            if verbose: print >> sys.stderr,"couldn't listtiffy result", sys.exc_type, sys.exc_value
            raise
        if verbose:
            print >> sys.stderr,"verbose expand result dump"
            print >> sys.stderr,"".join(result) # verbose
            print >> sys.stderr,"END OF EXPANDED RESULT DUMP" # verbose
        # return the text generated
        return result

def relativeEnvironment(env, relativeUrl):
    result = env.copy()
    result["SCRIPT_NAME"] = relativeUrl
    result["PATH_INFO"] = ""
    result[whiffenv.ENTRY_POINT] = relativeUrl
    return result

# note: wsgi is the callable!
__wsgi__ = expandPostedTemplate()
