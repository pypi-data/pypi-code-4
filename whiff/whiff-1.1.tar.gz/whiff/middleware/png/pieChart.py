
"KISS pie chart example class for PNG"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/png/pieChart - generate a PNG pie chart
{{/include}}

The <code>whiff_middleware/png/pieChart</code>
middleware generates a PNG image pie chart.
The pie chart generated is not fancy or feature rich.
This middleware is provided primarily to help illustrate
the use of WHIFF features, such as image link indirection.

"""

# copied and modified from skimpyGimpy distribution

import math
from skimpyGimpy import canvas # requires skimpyGimpy

# import must be absolute
from whiff.middleware import misc
from whiff import middleware
from whiff import resolver
from whiff import whiffenv

# for debug, set None if not debug
#DUMPFILEPATH = "/tmp/piechart.jpg"
DUMPFILEPATH = None

RSHADES = [0,64,122]
NRSHADES = len(RSHADES)
SHADES = range(0,256,64)
NSHADES = len(SHADES)

class PieChartBase:
    colors = [ (RSHADES[ i%NRSHADES],
                SHADES[ (i*3/2+2) % NSHADES],
                SHADES[ (i*5/4+3) % NSHADES])
               for i in range(25) ]
    fontPath = middleware.data_file_path("propell.bdf")
    fontScale = 1.0
    fontRadius = None
    fontMargin = 10
    labelColor = (255,0,0)
    labelInside = True
    labelMargin = 10

class PieChart(PieChartBase, misc.utility):
    # parameters come from cgi variables
    def __call__(self, env, start_response):
        env = resolver.process_cgi(env, parse_cgi=True)
        cgi_parameters = env[whiffenv.CGI_DICTIONARY]
        labelsAndData = cgi_parameters["labelsAndData"][0]
        labelsAndData = resolver.unquote(labelsAndData)
        self.labelsAndData = self.param_json(labelsAndData,env)
        radius = cgi_parameters["radius"][0]
        self.radius = self.param_json(radius,env)
        for param in dir(PieChartBase):
            if not param.startswith("__"):
                test = cgi_parameters.get(param)
                if test:
                    value = test[0]
                    json = self.param_json(value, env)
                    #pr "   setting require", param, json
                    setattr(self, param, json)
        c = self.drawCanvas()
        imagedata = c.dumpToPNG(DUMPFILEPATH)
        start_response("200 OK", [('Content-Type', 'image/png')])
        return [imagedata]
    def drawCanvas(this):
        c = canvas.Canvas()
        totalData = 0
        for (label, data) in this.labelsAndData:
            totalData += data
        radians = 0
        i = 0
        c.saveState()
        for (label, data) in this.labelsAndData:
            c.setCallBack("%s: %s" % (label, data))
            i += 1
            dataratio = data*1.0/totalData
            angle = 2*math.pi*dataratio
            endradians = radians + angle
            wedge = wedgePoints(radians, endradians, this.radius)
            color = this.colors[i % len(this.colors) ]
            c.setColorV(color)
            c.fillPolygon(wedge)
            radians = endradians
        c.restoreState()
        # do labels
        radians = 0
        c.addFont("f", this.fontPath)
        c.setFont("f", this.fontScale, this.fontRadius)
        if this.labelColor:
            c.setColorV(this.labelColor)
            for (label, data) in this.labelsAndData:
                dataratio = data*1.0/totalData
                angle = 2*math.pi*dataratio
                endradians = radians + angle
                midradians = radians + angle/2.0
                edgex = this.radius * math.cos(midradians)
                c.saveState()
                if edgex>=0: # or True:
                    c.rotateRadians(midradians)
                    if this.labelInside:
                        c.rightJustifyText(this.radius-this.labelMargin, 0, label)
                    else:
                        c.addText(this.radius + this.labelMargin, 0, label)
                else:
                    # don't show upside down labels
                    reverseRotation = midradians-math.pi
                    c.rotateRadians(reverseRotation)
                    if this.labelInside:
                        c.addText(-this.radius + this.labelMargin, 0, label)
                    else:
                        c.rightJustifyText(-this.radius-this.labelMargin, 0, label)
                c.restoreState()
                radians = endradians
        return c

def wedgePoints(startRadians, endRadians, radius, delta=math.pi/180):
    result = [ (0,0) ]
    if (endRadians<startRadians):
        raise ValueError, "end must be larger than start %s %s" % (
            endRadians,startRadians)
    nangles = int( (endRadians-startRadians)/delta)+2
    for i in range(nangles):
        angle = startRadians + (i-1)*delta
        x = math.cos(angle)*radius
        y = math.sin(angle)*radius
        result.append( (x,y) )
    return result


__middleware__ = PieChart

def test():
    import urllib
    from whiff.rdjson.jsonParse import format
    labelsAndData = [
        ("december", 30),
        ("january", 50),
        ("february", 40),
        ("march", 15),
        ("april", 64),
        ("may", 4),
        ("june", 49),
        ("july", 37),
        ]
    radius = 150
    D = {}
    D["labelsAndData"] = format(labelsAndData)
    D["radius"] = format(radius)
    D["labelColor"] = format((0,0,0))
    qs = urllib.urlencode(D)
    env = {
        "wsgi.url_scheme" : "http",
        "PATH_INFO" : "/whatever",
        "QUERY_STRING" : qs,
        "REMOTE_ADDR" : "127.0.0.1",
        "REMOTE_HOST" : "localhost",
        "REQUEST_METHOD" : "GET",
        "SCRIPT_NAME" : "",
        "SERVER_NAME" : "localhost",
        "SERVER_PORT" : "8888",
        "SERVER_PROTOCOL" : "HTTP/1.1",
        "SERVER_SOFTWARE" : "WSGIServer/0.1 Python/2.5",
        }
    app = PieChart()
    sresult = app(env, misc.ignore)
    result = "".join(list(sresult))
    print "test got", repr(result)
    if DUMPFILEPATH:
        print "written to", DUMPFILEPATH

if __name__=="__main__":
    test()

