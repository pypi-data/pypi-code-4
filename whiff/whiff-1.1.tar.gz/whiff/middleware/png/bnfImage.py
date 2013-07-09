
"""
Generate a railroad diagram for a BNF rule.
"""

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/png/bnfImage - generate a PNG image of a BNF railroad diagram
{{/include}}

The <code>whiff_middleware/png/bnfImage</code>
middleware generates a PNG image of a BNF railroad diagram.
The generated image is not fancy or feature rich.
This middleware is provided primarily to help illustrate
the use of WHIFF features, such as image link indirection.

"""

from skimpyGimpy import canvas # requires skimpyGimpy
from skimpyGimpy.railroad import bnf # requires skimpyGimpy

# import must be absolute
from whiff.middleware import misc
from whiff.middleware import data_file_path

class bnfImage(misc.utility):
    def __init__(self, page):
        self.page = page
    def __call__(self, env, start_response):
        bnftext = self.param_value(self.page, env).strip()
        fontdir = data_file_path("")
        c = bnf.getc(fontdir)
        [target, body] = bnftext.split("::=")
        target = target.strip()
        body = body.strip()+" " # extra whitespace to avoid a bug...
        #pr "parsing body", body
        (definition, cursor) = bnf.alternatives([], 0, body, c)
        if cursor<len(body):
            raise ValueError, "not all of body consumed "+repr(body[cursor:])
        diagram = bnf.Define(target, definition, c)
        diagram.drawAt(0,0)
        imagedata = c.dumpToPNG(None)
        start_response("200 OK", [('Content-Type', 'image/png')])
        return [imagedata]        

__middleware__ = bnfImage

def test(dumpfile="/tmp/bnf.png"):
    app = bnfImage('apple ::= (oranges | "peaches")* animals')
    data = "".join(app({}, misc.ignore))
    file(dumpfile, "wb").write(data)
    print "test dumped to", dumpfile

if __name__=="__main__":
    test()
