
"""
Generate a Schema diagram from a json spec.
Example:
    [
    ["table", "emp", ["enum"], ["name", "BD"], 100, 100],
    ["table", "dept", ["dnum"], ["dname", "type", "mgrenum"], 100, 100],
    ["foreign", "dept", ["mgrenum"] "emp", true, 0, 1]
    ]
"""


whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/png/schemaDiagram - generate a PNG image of relational database schema
{{/include}}

The <code>whiff_middleware/png/schemaDiagram</code>
middleware generates a PNG image of a relational database schema.
The generated image is not fancy or feature rich.
This middleware is provided primarily to help illustrate
the use of WHIFF features, such as image link indirection.

"""

#from whiff.middleware import ERdiagram
from skimpyGimpy import canvas # requires skimpyGimpy
from skimpyGimpy.erd import schema # requires skimpyGimpy
from skimpyGimpy.erd import table # requires skimpyGimpy
from skimpyGimpy.railroad import bnf # requires skimpyGimpy

# import must be absolute
from whiff.middleware import misc
from whiff.middleware import data_file_path
from whiff import whiffenv
from whiff.rdjson import jsonParse

def upperLeftSchema(s):
    "this is a hack which should be added to skimpyGimpy."
    for t in s.nameToTable.values():
        upperLeftTable(t)

def upperLeftTable(t):
    cfg = t.cfg
    d = cfg.delta
    t.compute_geometry()
    h = t.gh * d
    (x,y) = t.p
    t.p = (x, y-h)
    # unmark geometry to force recompute.
    t.gw = t.gh = None

class SchemaDiagram(misc.utility):
    def __init__(self, page, javascript=False, xmax=None, ymax=None):
        self.page = page
        self.javascript = javascript
        self.xmax = xmax
        self.ymax = ymax
    def __call__(self, env, start_response):
        """Generate schema from specification page"""
        spec = self.param_json(self.page, env)
        javascript = self.param_json(self.javascript, env)
        xmax = self.param_json(self.xmax, env)
        ymax = self.param_json(self.ymax, env)
        fontdir = data_file_path("")
        c = bnf.getc(fontdir)
        if xmax and ymax:
            c.crop(0,0,xmax,ymax)
            # put tiny black dots around border
            c.setColor(0,0,0)
            c.addRect(0,0,1,1)
            c.addRect(xmax-1,ymax-1,1,1)
            c.addRect(xmax-1,0,1,1) 
            c.addRect(0,ymax-1,1,1)
        nameToAttributes = {}
        nameToKeys = {}
        nameAndAttributeGroups= {}
        foreignKeyInfo = []
        S = schema.Schema(c)
        for directive in spec:
            #pr "directive", directive
            indicator = directive[0]
            if indicator=="table":
                [indicator, name, keys, otherAtts, x, y] = directive
                keys = table.normalizeAttributes(keys)
                S.addTable(name, x, y)
                S.addPrimaryKey(name, keys)
                nameToKeys[name] = keys
                nameAndAttributeGroups[(name,keys)] = 1
                otherAtts = table.normalizeAttributes(otherAtts, keys)
                nameToAttributes[name] = otherAtts
            elif indicator=="foreign":
                [indicator, name, atts, otherName, required, minimum, maximum] = directive
                atts = table.normalizeAttributes(atts)
                #pr "foreign key info", (name, atts, otherName)
                foreignKeyInfo.append((name, atts, otherName, required, minimum, maximum))
            else:
                raise ValueError, "unknown indicator "+repr(indicator)
        # now set up the attribute groups for the tables
        for (name, atts, othername, required, minimum, maximum) in foreignKeyInfo:
            ng = (name, atts)
            if not nameAndAttributeGroups.has_key(ng):
                S.addFieldGroup(name, atts)
                nameAndAttributeGroups[ng] = 1
        # find ungrouped attributes
        nameAndAttribute = {}
        allatts = {}
        for (name, group) in nameAndAttributeGroups.keys():
            #pr "name, group", (name, group)
            for att in group:
                nameAndAttribute[(name, att)] = 1
        # assign attribute groups for other attributes
        for (name, attributes) in nameToAttributes.items():
            ungrouped = []
            for att in attributes:
                if not nameAndAttribute.has_key( (name, att) ):
                    ungrouped.append(att)
            if ungrouped:
                S.addFieldGroup(name, ungrouped)
        # declare the foreign keys
        for (name, atts, othername, required, minimum, maximum) in foreignKeyInfo:
            #pr "adding foreign key", (name,atts,othername,required,minimum,maximum)
            tomin = 0
            if required:
                tomin=1
            tomax = 1
            frommin = minimum
            frommax = maximum
            S.addForeignKey(name, atts, othername, frommin=frommin, tomin=tomin, frommax=frommax, tomax=tomax)
        # deliver the payload
        upperLeftSchema(S)
        S.draw()
        if javascript:
            # XXXX hard coded constants...
            imageId = str(whiffenv.getName(env, "Schema"))
            callbackFunction = str(whiffenv.getName(env, "SchemaCallBack"))
            imagedata = c.dumpJavascript(None, imageId, callbackFunction)
            tablesName = str(whiffenv.getName(env, "Tables"))
            tablesDict = {}
            for (name, keys) in nameToKeys.items():
                other = nameToAttributes[name]
                tablesDict[name] = tuple(keys) + tuple(other)
            tablesList = tablesDict.items()
            tablesList.sort()
            start_response("200 OK", [('Content-Type', 'application/javascript')])
            yield tablesName
            yield " = "
            yield jsonParse.format(tablesList)
            yield ";\n\n"
        else:
            imagedata = c.dumpToPNG(None)
            start_response("200 OK", [('Content-Type', 'image/png')])
        yield imagedata

__middleware__ = SchemaDiagram

def test(dumpfile="/tmp/schema.png"):
    spec = """
    [
    ["table", "emp", ["enum"], ["name", "BD"], 100, 100],
    ["table", "dept", ["dnum"], ["dname", "type", "mgrenum"], 300, 100],
    ["foreign", "dept", ["mgrenum"], "emp", true, 0, 1]
    ]
    """
    app = SchemaDiagram(spec)
    data = "".join(app({}, misc.ignore))
    file(dumpfile, "wb").write(data)
    print "test dumped to", dumpfile

if __name__=="__main__":
    test()
        
