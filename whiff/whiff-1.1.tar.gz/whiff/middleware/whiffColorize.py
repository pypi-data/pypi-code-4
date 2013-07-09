
"""
Colorize text as html using pygments
"""

whiffCategory = "tools"

import types
import pygments  # this middleware requires Pygments!
from pygments.lexers import get_lexer_by_name
import pygments.token
from pygments.formatters import HtmlFormatter


whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/whiffColorize - colorize WHIFF source embedded in HTML (or other format)
{{/include}}

The <code>whiff_middleware/whiffColorize</code>
middleware converts WHIFF text embedded in HTML text into an HTML colorized format.
It is also possible to colorize WHIFF embedded in any other format supported by
Pygments.  This middleware requires the Pygments package which must be installed
separately and is not automatically installed.  The colorized output HTML uses
CSS classes defined in the <code>PygmentsCSS</code> stylesheet.
"""

# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv
from whiff import resolver
# environment key which may name the css class
from whiff.middleware.pygmentsCss import envCssClassName
from whiff.middleware.pygmentsCss import defaultCssClassName
# environment key which may name the pygments lexer
envLexerName = "pygmentsCss.lexer"

class whiffColorize(misc.utility):
    def __init__(self, page, lexer=None, cssClass=None):
        self.page = page
        self.lexer = lexer
        self.cssClass = cssClass
    def __call__(self, env, start_response):
        cssClassName = lexerName = None
        # find css class
        if self.cssClass:
            cssClassName = self.param_value(self.cssClass, env)
        else:
            # check for environment entry
            cssClassName = env.get(envCssClassName)
        if cssClassName is None:
            cssClassName = defaultCssClassName
        # find lexer (no default)
        if self.lexer:
            lexerName = self.param_value(self.lexer, env)
        else:
            # check environment
            lexerName = env.get(envLexerName)
        if lexerName is None:
            raise ValueError, "lexer name must be specified either as a require or in the environment"
        # get the TEXT of the page (NOT EXPANDED)
        code = self.param_value(self.page, env)
        #pr "code is", repr(code)
        lexer = get_lexer_by_name(lexerName, stripall=False, stripnl=False, encoding="utf8")
        formatter = HtmlFormatter(linenos=False, cssclass=cssClassName)
        if type(code) is not types.UnicodeType:
            code = unicode(code, "utf8", "ignore")
        payload = whiff_highlight(code, lexer, formatter)
        start_response("200 OK", [('Content-Type', 'text/css')])
        return [payload]

def whiff_highlight(code, lexer, formatter):
    stream = whiff_lex(code, lexer)
    return pygments.format(stream, formatter)

def nuke_final_newline(stream, text):
    "get rid of extra newline at the end if present... (yuck)"
    stream = list(stream)
    if stream and text and text[-1]!="\n":
        last = stream[-1]
        (tk, tx) = last
        if tx and tx[-1]=="\n":
            tx = tx[:-1]
            if tx:
                stream[-1] = (tk, tx)
            else:
                del stream[-1]
    #pr "nuked", stream
    return stream

def whiff_lex(code, lexer):
    "parse stuff outside of {{}} using lexer, inside using javascript lexer"
    from whiff import stream
    code = stream.myunicode(code)
    js_lexer = get_lexer_by_name("javascript", stripall=False, stripnl=False)
    scode = code.split("{{")
    index = 0
    nscode = len(scode)
    if nscode<1:
        return
    outside_code = scode[index]
    for x in nuke_final_newline(pygments.lex(outside_code, lexer), outside_code):
        #pr "yield", x
        yield x
    index += 1
    while index<nscode:
        chunk = scode[index]
        schunk = chunk.split("}}", 1)
        #pr "schunk", schunk
        inside_code = schunk[0]
        is_comment = False
        if inside_code.startswith("comment"):
            is_comment = True
        outside_code = None
        if len(schunk)>1:
            outside_code = schunk[1]
            #inside_code = "{{" + inside_code + "}}"
        else:
            #inside_code = "{{" + inside_code
            pass
        if is_comment:
            comment = "{{"+inside_code
            if outside_code is not None:
                comment = comment+"}}"
            x = (pygments.token.Token.Comment, comment)
            #pr "yield", x
            yield x
        else:
            inside_split = inside_code.split(None, 1)
            head = "{{"+inside_split[0]
            x = (pygments.token.Token.Name.Function, head)
            #pr "yield", x
            yield x
            slash = False
            if len(inside_split)>1 and inside_split[1]:
                x = (pygments.token.Token.Text, u" ")
                #pr "yield", x 
                yield x
                remainder = inside_split[1]
                if remainder.endswith("/"):
                    slash = True
                    remainder = remainder[:-1]
                #pr "parsing javascript", repr(remainder)
                jslex = nuke_final_newline(pygments.lex(remainder, js_lexer), remainder)
                for x in jslex:
                    ##pr "jsyield", x
                    yield x
                #pr "done with javascript"
            if outside_code is not None:
                if slash:
                    x = (pygments.token.Token.Name.Function, u"/}}")
                else:
                    x = (pygments.token.Token.Name.Function, u"}}")
                #pr "yield", x
                yield x
        if outside_code:
            #pr "outside code", repr(outside_code)
            for x in nuke_final_newline(pygments.lex(outside_code, lexer), outside_code):
                #pr "yield", x
                yield x
            #pr "done with outside code"
        index += 1

__middleware__ = whiffColorize

def test():
    txt = "{{comment : whiff comment/}} {{get-env name/}} <h1>hello</h1>"
    app = whiffColorize(txt, "html", "cssClass")
    x = app({}, misc.ignore)
    print "txt", repr(txt)
    print "".join(x)

if __name__=="__main__":
    test()
    
