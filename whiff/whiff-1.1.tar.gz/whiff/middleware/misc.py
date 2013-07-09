
whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff.middleware.misc - miscellaneous support module
{{/include}}

The <code>misc</code>
module is not a middleware -- it is a module
that provides miscellaneous support functions
to other middleware modules.
"""

import types
from whiff.rdjson import jsonParse
#from whiff import page
from whiff import stream
from whiff import whiffenv
import urlparse
import wsgiref.util
from whiff import stream

class utility:
    "common functionality used by javascript generation middlewares"
    component_headers = None
    def my_start_response(self, status, headers):
        "for evaluating sub-components -- check for status 200, record headers"
        if self.component_headers is None:
            self.component_headers = []
        self.component_headers.extend(headers)
        sstatus = status.split()
        if not sstatus or sstatus[0]!="200":
            raise ValueError, "bad status from sub-component "+repr(status)
    def component_content_type(self):
        result = None
        ch = self.component_headers
        if ch:
            for (name,value) in ch:
                if name.lower()=="content-type":
                    value = value.lower()
                    if result is not None and result!=value:
                        raise ValueError, "ambiguous component content types "+repr((result, value))
                    result = value
        return result
    def derive_headers(self, content_type):
        result_headers = []
        ch = self.component_headers
        if ch:
            for (name, value) in ch:
                name = str(name)
                if name.lower()!="content-type":
                    result_headers.append( (name, value) )
        result_headers.append( ('Content-Type', content_type) )
        return result_headers
    def param_json(self, param, env, start_response=None):
        "try to interpret require as a json value (list or dict)"
        if start_response is None:
            start_response = self.my_start_response
        return streamOrDataToData(param, env, start_response)
    def param_value(self, param, env, start_response=None):
        "evaluate a require, which may be a sub-stream or a page"
        if start_response is None:
            start_response = self.my_start_response
        return streamOrStringToString(param, env, start_response)
    def param_binary(self, param, env, start_response=None):
        "evaluate a require, which may be a sub-stream or a page"
        if start_response is None:
            start_response = self.my_start_response
        return streamOrStringToBinary(param, env, start_response)
    def deliver_page(self, string_or_page, env, start_response, default_mime="text/html"):
        pt = type(string_or_page)
        if pt in whiffenv.JSON_TYPES:
            string_or_page = jsonParse.format(string_or_page)
            pt = type(string_or_page)
        if whiffenv.isAString(string_or_page):
            headers = self.derive_headers(default_mime)
            #pr "deliver page starting response for string sequence", start_response
            start_response("200 OK", headers)
            return stringsOnly([string_or_page])
        else:
            #pr "deliver page calling string_or_page=", string_or_page
            return stringsOnly(string_or_page(env, start_response))
    def deliver_json(self, object_or_page, env, start_response, default_mime="application/javascript"):
        json = self.param_json(object_or_page, env)
        text = jsonParse.format(json)
        return self.deliver_page(text, env, start_response, default_mime)
    def param_text(self, param):
        return param_as_text(param)

def stringsOnly(sequence, StringType=types.StringType, UnicodeType=types.UnicodeType):
    for x in sequence:
        tx = type(x)
        if tx is StringType:
            yield x
        elif tx is UnicodeType:
            yield stream.mystr(x)
        else:
            yield str(x)

def param_as_text(param):
    if param is None:
        return None
    elif type(param) in types.StringTypes:
        return param
    else:
        return param.text # for stream or page:

class javaScriptGenerator(utility):
    "utility generating javascript"
    # currently same as utility

def jsListFromString(text, linebreak="\n"):
    "break a text readably into a json list with reasonable line lengths"
    listResult = list(jsListFromStringGenerator(text))
    return linebreak.join(listResult)

def jsListFromStringGenerator(text, maxlen=80):
    yield "["
    lines = text.split("\n")
    inside = False
    nlines = len(lines)
    count = 0
    for line in lines:
        count += 1
        while len(line)>maxlen:
            chunk = line[:maxlen]
            line = line[maxlen:]
            chunkFormatted = jsonParse.formatString(chunk)
            if inside:
                yield ","+chunkFormatted
            else:
                yield chunkFormatted
                inside = True
        if count==nlines:
            # don't add newline
            lineFormatted = jsonParse.formatString(line)
        else:
            # add back newline within formatted string
            lineFormatted = jsonParse.formatString(line+"\n")
        if inside:
            yield ","+lineFormatted
        else:
            yield lineFormatted
            inside = True;
    yield "]"

# maybe this should be available from the whiff main module?

def ignore(*args):
    "ignore calls to this function"
    return args

def streamOrStringToBinary(thing, env, start_response=ignore):
    "if the string is a stream return stream evaluation as 8-bit string, if string return it as 8-bit, otherwise error"
    if thing is None:
        return None
    if type(thing) in types.StringTypes:
        return stream.mystr(thing)
    else: # elif isinstance(thing, stream.StreamApp):
        # try to interpret it as a WSGI app
        contentSequence = thing(env, start_response)
        contentList = list(contentSequence)
        contentList = map(stream.mystr, contentList)
        result = "".join(contentList)
        return result

def streamOrStringToString(thing, env, start_response=ignore):
    "if the string is a stream return stream evaluation as unicode string, if string return it as unicode, otherwise error"
    if thing is None:
        return None
    if type(thing) in types.StringTypes:
        return stream.myunicode(thing)
    else: # elif isinstance(thing, stream.StreamApp):
        # try to interpret it as a WSGI app
        contentSequence = thing(env, start_response)
        contentList = list(contentSequence)
        contentList = map(stream.myunicode, contentList)
        result = u"".join(contentList)
        return result
    #else:
    #    raise ValueError, "expected stream, string, or unicode, got "+repr((type(thing),thing))

def streamOrDataToData(thing, env, start_response=ignore):
    "if a value is a known json type, leave it alone -- otherwise try to eval as wsgi and parse json"
    # note: for these purposes strings are not treated as json types
    tt = type(thing)
    if tt in whiffenv.JSON_TYPES:
        return thing
    else:
        s = streamOrStringToString(thing, env, start_response)
        #pr "NOW PARSING JSON"
        #pr s
        (flag, value, cursor) = jsonParse.parseValue(s)
        if flag:
            return value
        c1 = s[max(0,cursor-20):cursor]
        c2 = s[cursor: cursor+20]
        raise ValueError, "could not parse json data "+repr((cursor, value, c1, c2))

def getAbsoluteUrl(url, environ):
    """make an absolute URL from a relative one, wrt the WSGI environment"""
    uri = wsgiref.util.request_uri(environ, False)
    absoluteUrl = urlparse.urljoin(uri, url)
    return absoluteUrl

def regenerate(generator):
    """
    This is a bit of a hack to force wsgi applications to start the response without generating the whole response...
    """
    tg = type(generator)
    if tg is types.ListType or tg is types.TupleType:
        return generator
    generator = iter(generator)
    current_element = generator.next()
    return regenerate1(generator, current_element)

def regenerate1(generator, current_element):
    yield current_element
    for next_element in generator:
        current_element = next_element
        yield current_element

def test_regenerate():
    x = list(regenerate(iter(xrange(10))))
    assert x==range(10)

