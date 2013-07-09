
"""
test HTML text for acceptible tags, attributes, and values for attributes.

Put html stripped of evil in strippedVariable.
Put deletion explanations, if any in deletionsVariable
"""

whiffCategory = "formatting"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/TestSafeHtml - test/strip dangerous HTML tags from text
{{/include}}

The <code>whiff_middleware/TestSafeHtml</code>
middleware looks for dangerous HTML constructs in an
HTML text.  If dangerous tags are found the report of
complaints will be placed in the <code>whiff.middleware.deletedhtml</code>
environment entry (by default).  The HTML stripped of any unsafe constructs
will be placed in the
<code>whiff.middleware.safehtml</code> environment entry
(by default).

{{include "example"}}
{{using targetName}}TestSafeHtml{{/using}}
{{using page}}

{{include "whiff_middleware/TestSafeHtml"}}
    {{using html}}
        <h1>hello there!</h1>
        <script> alert("purple dinosour!"); </script>
    {{/using}}
    {{using page}}
        Here is the stripped HTML
        <hr>
        {{get-env whiff.middleware.safehtml/}}
        <hr>
        The HTML had the following problems
        <pre>{{get-env whiff.middleware.deletedhtml}}no problems{{/get-env}}
        </pre>
    {{/using}}
{{/include}}

{{/using}}
{{/include}}

"""

from whiff.middleware import misc

STRIPPED_VARIABLE = "whiff.middleware.safehtml"
DELETIONS_VARIABLE = "whiff.middleware.deletedhtml"

GOODTAGS = ["a", "abbr", "acronym", "address", "b", "big", "blockquote", "br", "center", "cite", "code",
            "dd", "del", "dir", "div", "dl", "dt", "em", "font", "hr", "h1", "h2", "h3", "h4", "h5", "h6", "i", "ins",
            "kbd", "li", "marquee", "menu", "nobr", "noembed", "ol", "p", "pre", "q", "rt", "ruby", "rbc", "rb", "rtc", "rp",
            "s", "samp", "small", "span", "strike", "strong", "sub", "sup", "tt", "u", "ul", "var", "xmp", "img", "embed",
            "object", "table", "tr", "td", "th", "tbody", "caption", "thead", "tfoot", "colgroup", "col"]

GOODATTRIBUTES = ["abbr", "accept", "accesskey", "align", "alink", "alt", "axis", "background",
                  "bgcolor", "border", "cellpadding", "cellspacing", "char", "charoff", "charset", "checked", "cite", "class", "classid",
                  "clear", "color", "cols", "colspan", "compact", "content", "coords", "datetime", "dir", "disabled", "enctype", "face",
                  "for", "header", "height", "href", "hreflang", "hspace", "id", "ismap", "label", "lang", "longdesc", "maxlength", "multiple",
                  "name", "noshade", "nowrap", "profile", "readonly", "rel", "rev", "rows", "rowspan", "rules", "scope", "selected", "shape",
                  "size", "span", "src", "start", "style", "summary", "tabindex", "target", "text", "title", "type", "usemap", "valign",
                  "value", "vlink", "vspace", "width"]

EVILVALUES = ["javascript:", "behavior:", "vbscript:", "mocha:", "livescript:", "expression"]

class SafeHtml(misc.utility):
    def __init__(self,
                 html,
                 page,
                 goodTags = GOODTAGS,
                 goodAttributes = GOODATTRIBUTES,
                 evilValues = EVILVALUES,
                 strippedVariable = STRIPPED_VARIABLE,
                 deletionsVariable = DELETIONS_VARIABLE,
                 ):
        self.html = html
        self.page = page
        self.goodTags = goodTags
        self.goodAttributes = goodAttributes
        self.evilValues = evilValues
        self.strippedVariable = STRIPPED_VARIABLE
        self.deletionsVariable = DELETIONS_VARIABLE
    def __call__(self, env, start_response):
        html = self.param_value(self.html, env)
        strippedVariable = self.param_value(self.strippedVariable, env)
        deletionsVariable = self.param_value(self.deletionsVariable, env)
        goodTags = self.param_json(self.goodTags, env)
        goodAttributes = self.param_json(self.goodAttributes, env)
        evilValues = self.param_json(self.evilValues, env)
        J = Judge(goodTags, goodAttributes, evilValues)
        goodhtml = genjoin( J.split(html) )
        complaints = list( J.split(html, good=False) )
        env = env.copy()
        env[strippedVariable] = goodhtml
        if complaints:
            env[deletionsVariable] = complaints
        return self.deliver_page(self.page, env, start_response)
        
def genjoin(gen):
    return "".join(list(gen))

def lno(text, cursor):
    pre = text[:cursor]
    sp = pre.split("\n")
    return len(sp)

class Judge:
    def __init__(self,
                 goodTags = GOODTAGS,
                 goodAttributes = GOODATTRIBUTES,
                 evilValues = EVILVALUES,
                 ):
        gt = self.goodTags = {}
        for g in goodTags:
            gt[g] = g
        ga = self.goodAttributes = {}
        for a in goodAttributes:
            ga[a] = a
        self.evilValues= evilValues
    def split(self, text, good=True):
        "generate either the good segments with bad segments stripped, or the sequence of complaints"
        #pr "adulterating text"
        #text = "."+text+"."
        #pr "adulterated "+repr(text)
        bad = not good
        from xml.etree.cElementTree import fromstring
        gt = self.goodTags
        ga = self.goodAttributes
        ev = self.evilValues
        # scan for tag begins or ends and parse as xml bodyless tags
        cursor = 0
        done = False
        ltext = len(text)
        # if good, dangerous looking tags will have their heads lopped off... (matching end tags will remain)
        while not done and cursor<ltext:
            startcursor = cursor
            tagstart = text.find("<", cursor)
            if good and tagstart>0:
                #pr "yielding up to tag start", (cursor, tagstart, text[cursor:tagstart])
                yield text[cursor:tagstart]
            if tagstart<cursor:
                done = True
            else:
                chunkstart = tagstart+1
                tagend = text.find(">", chunkstart)
                if tagend<chunkstart:
                    cursor = tagstart
                    #pr "no close bracket", (cursor, chunkstart, text[cursor:])
                    done = True
                    tagend = len(text)
                else:
                    chunk = tagchunk = text[chunkstart:tagend]
                    chunkok = True # innocent until proven guilty
                    cursor = tagend+1
                    if tagchunk.startswith("/"):
                        tagchunk = tagchunk[1:]
                    elif tagchunk.endswith("/"):
                        tagchunk = tagchunk[:-1]
                    # construct and parse a fake tag
                    xmltag = "<%s/>" % tagchunk
                    xmltag = xmltag.replace("&", "&amp;")
                    #pr "checking", xmltag
                    try:
                        node = fromstring(xmltag)
                    except:
                        chunkok = False
                        #pr "xml parse failed", xmltag
                        if bad:
                            yield "near line %s could not understand tag starting %s" % (lno(text,chunkstart), repr(tagchunk[:50]))
                    else:
                        # check tag name
                        tagname = node.tag.lower()
                        if not gt.has_key(tagname):
                            chunkok = False
                            #pr "bad tag name", tagname
                            if bad:
                                yield "tag name %s not recognized as safe at line %s" % (repr(tagname), lno(text, chunkstart))
                        else:
                            # check attribute name
                            for (attname, attvalue) in node.attrib.items():
                                attvalue = attvalue.strip()
                                if not ga.has_key(attname):
                                    chunkok = False
                                    #pr "bad attribute", attname
                                    if bad:
                                        yield "in tag %s the attribute %s is not recognized as safe at line %s" % (repr(tagname), repr(attname), lno(text,chunkstart))
                                elif attvalue:
                                    # check attribute value
                                    for badvalue in ev:
                                        if attvalue.startswith(badvalue):
                                            chunkok = False
                                            #pr "bad value", badvalue
                                            if bad:
                                                yield "in tag %s the attribute value %s is considered dangerous at line %s" %(repr(tagname), repr(attvalue),
                                                                                                                         lno(text, chunkstart))
                    if chunkok:
                        if good:
                            #pr "sending ok chunk", repr(chunk)
                            yield "<"
                            yield chunk
                            yield ">"
                    elif good:
                        #pr "quoting bad chunk"
                        yield "&lt;"
                        yield chunk
                        yield "&gt;"
        if good:
            if cursor<ltext:
                #pr "yielding remainder", (cursor, text[cursor:])
                yield text[cursor:]
        #pr "SAFE HTML FILTER COMPLETE"

__middleware__ = SafeHtml

# === testing...

TESTHTML = """
<script>
alert('hi there');
</script>
<h1> header </h1>

<blockquote>
<a onclick="alert('hello')"> <br>
<a href="nextpage"> <br>
<a href='previous page'> <br>
<a href="javascript:alert('hello')"> <hr>
</blockquote>
"""

TESTHTML = "1<2>>3<6"

def testJudge():
    print "testing"
    print TESTHTML
    J = Judge()
    print "testing good"
    for x in J.split(TESTHTML):
        print "good", repr(x)
    print
    print "testing bad"
    for x in J.split(TESTHTML, good=False):
        print "BAD", repr(x)
    print
    print "join of good text"
    print "====="
    print "".join(list(J.split(TESTHTML)))
    print "====="

if __name__=="__main__":
    testJudge()
