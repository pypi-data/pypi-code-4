
"""
Generate an ER diagram from a json specification
Example specification: (see test(...) function below).
"""


whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/png/ERdiagram - generate a PNG image of an Entity-Relationship diagram
{{/include}}

The <code>whiff_middleware/png/ERdiagram</code>
middleware generates a PNG image of an Entity-Relationship diagram.
The generated image is not fancy or feature rich.
This middleware is provided primarily to help illustrate
the use of WHIFF features, such as image link indirection.

"""


from skimpyGimpy import canvas # requires skimpyGimpy
from skimpyGimpy.erd import drawing # requires skimpyGimpy
from skimpyGimpy.railroad import bnf # requires skimpyGimpy

# import must be absolute
from whiff.middleware import misc
from whiff.middleware import data_file_path
from whiff import whiffenv
from whiff.rdjson import jsonParse
from whiff import gateway

class ERdiagram(misc.utility):
    def __init__(self, page, javascript=False, xmax=None, ymax=None,
                 adjust=False, rulePath=["local", "Rule"]):
        self.page = page
        self.javascript = javascript
        self.xmax = xmax
        self.ymax = ymax
        self.adjust = adjust
        self.rulePath = rulePath
    def __call__(self, env, start_response):
        spec = self.param_json(self.page, env)
        javascript = self.param_json(self.javascript, env)
        xmax = self.param_json(self.xmax, env)
        ymax = self.param_json(self.ymax, env)
        adjust = self.param_json(self.adjust, env)
        #pr "ERdiagram adjust=", repr(adjust)
        rulePath = self.param_json(self.rulePath, env)
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
        d = drawing.Drawing(c)
        attributes = []
        entities = []
        relationships = []
        participants = {}
        #pr "got specs", spec
        for directive in spec:
            indicator = directive[0]
            if indicator=="entity":
                (indicator, name, x,y, weak) = directive
                d.addEntity(name, x, y, weak=weak)
                entities.append((name, weak))
            elif indicator=="relationship":
                (indicator, name, x,y, weak) = directive
                d.addRelationship(name, x, y, weak=weak)
                relationships.append((name, weak))
            elif indicator=="participate":
                (indicator, entityName, relName, rolename,  minimum, maximum) = directive
                d.participate(entityName, relName, rolename, minimum, maximum)
                rpart = participants.get(relName, {})
                rpart[entityName] = 1
                participants[relName] = rpart
                participants[entityName] = relName
            elif indicator=="attribute":
                (indicator, aName, name, x,y, iskey) = directive
                d.addAttribute(aName, name, x,y, iskey=iskey)
                attributes.append(name)
            else:
                raise ValueError, "unknown indicator "+repr(indicator)
        upperLeftCorners(d)
        if spec and adjust:
            d.adjust()
            spec = d.dumpList()
        # store the (adjusted) spec as a resource in case other component needs to use the value
        gateway.putResource(env, rulePath, spec)
        d.prepare()
        d.draw()
        if javascript:
            # xxxx something should be done about hard coded constants here
            imageId = str(whiffenv.getName(env, "ERDiagram"))
            callbackFunction = str(whiffenv.getName(env, "ERDiagramCallBack"))
            imagedata = c.dumpJavascript(None, imageId, callbackFunction)
            entitiesName = str(whiffenv.getName(env, "EREntities"))
            relationshipsName = str(whiffenv.getName(env, "ERRelationships"))
            attributesName = str(whiffenv.getName(env, "ERAttributes"))
            participantsName = str(whiffenv.getName(env, "ERParticipants"))
            start_response("200 OK", [('Content-Type', 'application/javascript')])
            for (name, value) in [(entitiesName, entities),
                                  (relationshipsName, relationships),
                                  (attributesName, attributes),
                                  (participantsName, participants)]:
                yield name
                yield " = "
                yield jsonParse.format(value)
                yield ";\n\n"
        else:
            imagedata = c.dumpToPNG(None)
            start_response("200 OK", [('Content-Type', 'image/png')])
        yield imagedata        

def upperLeftCorners(d):
    "this is a hack which should be added to skimpyGimpy."
    for e in d.nameToEntity.values():
        #pr "adjusting entity", e
        upperLeftCorner(e)
    for r in d.nameToRelationship.values():
        #pr "adjusting relationship", r
        upperLeftCorner(r)
    for (a, p) in d.namesToAttributeAndPath.values():
        #pr "adjusting attr", a
        upperLeftCorner(a)

def upperLeftCorner(e):
    "this is a hack which should be added to skimpyGimpy."
    cfg = e.cfg
    d = cfg.delta
    h = e.gh * d
    (x,y) = e.p
    e.p = (x, y-h)

__middleware__ = ERdiagram

def test(dumpfile="/tmp/bnf.png"):
    spec = """
    [
    ["entity", "emp", 0,0, false],
    ["entity", "dept", 300,0, false],
    ["entity", "dependent", -300,0, true],
    ["relationship", "dep_of", -150, 0, true],
    ["relationship", "manages", 150, 0, false],
    ["participate", "emp", "manages", "manager", 0, "many"],
    ["participate", "emp", "manages", "manager2", 0, "many"],
    ["participate", "dept", "manages", "managed", 1, 1],
    ["participate", "emp", "dep_of", "primary", 0, "many"],
    ["participate", "dependent", "dep_of", "sub", 1, 1],
    ["attribute", "enum", "emp", 0,100, true]
    ]
    """
    app = ERdiagram(spec)
    data = "".join(app({}, misc.ignore))
    file(dumpfile, "wb").write(data)
    print "test dumped to", dumpfile

if __name__=="__main__":
    test()
        
