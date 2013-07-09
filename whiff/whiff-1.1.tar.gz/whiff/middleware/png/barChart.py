
"KISS bar chart example class for PNG"


whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/png/barChart - generate a PNG bar chart
{{/include}}

The <code>whiff_middleware/png/barChart</code>
middleware generates a PNG image bar chart.
The bar chart generated is not fancy or feature rich.
This middleware is provided primarily to help illustrate
the use of WHIFF features, such as image link indirection.

"""


# copied and modified from skimpyGimpy distribution

from skimpyGimpy import canvas # requires skimpyGimpy

# import must be absolute
from whiff.middleware import misc
from whiff import middleware
from whiff import resolver
from whiff import whiffenv

# for debug, set None if not debug
#DUMPFILEPATH = "/tmp/barchart.jpg"
DUMPFILEPATH = None

class BarChartBase:
    axisColor = (0xff, 0, 0)
    labelColor = (0, 0xff, 0)
    barColor = (0, 0, 0xff)
    fontPath = middleware.data_file_path("propell.bdf")
    barWidth = 20
    barSeparation = 10
    barMaxHeight = 200
    fontScale = 1.0
    fontRadius = None
    fontMargin = 10
    axisWidth = 1
    tickFormat = "%4.2f"
    tickShift = 5
    #lowerLeft = (-100,-100)
    #upperRight = (300, 300)

class BarChart(BarChartBase, misc.utility):
    # all parameters come from cgi variables
    
    def __call__(self, env, start_response):
        #pr "calling BarChart"
        env = resolver.process_cgi(env, parse_cgi=True)
        cgi_parameters = env[whiffenv.CGI_DICTIONARY]
        labelsAndData = cgi_parameters["labelsAndData"][0]
        labelsAndData = resolver.unquote(labelsAndData)
        self.labelsAndData = self.param_json(labelsAndData,env)
        axisDelta = cgi_parameters["axisDelta"][0]
        self.axisDelta = self.param_json(axisDelta,env)
        for param in dir(BarChartBase):
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
    def drawCanvas(self):
        c = canvas.Canvas()  
        #c.setBackgroundColor(0,0,0)
        #c.setBackgroundCallback("out")
        #c.setCallBack("not on data")
        #((xm,ym), (xM, yM)) = (self.lowerLeft, self.upperRight)
        #c.crop(xm,ym,xM,yM)
        c.addFont("f", self.fontPath)
        c.setFont("f", self.fontScale, self.fontRadius)
        # draw labels
        c.saveState()
        c.rotate(-90)
        c.setColorV(self.labelColor)
        y = self.barSeparation
        maxdata = 0
        for (label, data) in self.labelsAndData:
            #c.setCallBack("%s: %s" % (data, label))
            c.addText(self.fontMargin,y, label)
            maxdata = max(data, maxdata)
            y = y+self.barSeparation+self.barWidth
        # draw bars
        c.setColorV(self.barColor)
        y = self.barSeparation
        for (label, data) in self.labelsAndData:
            c.setCallBack("%s: %s" % (label, data))
            barlength = (data*self.barMaxHeight)/maxdata
            c.addRect(-barlength,y,barlength,self.barWidth)
            y = y+self.barSeparation+self.barWidth
        c.restoreState()
        # draw axis
        c.setColorV(self.axisColor)
        c.addLine( (0,0), (0,self.barMaxHeight) )
        c.addLine( (0,0), (self.barSeparation+len(self.labelsAndData)*(self.barSeparation+self.barWidth), 0))
        mark = self.axisDelta
        while mark<maxdata:
            c.setColorV(self.axisColor)
            y = (mark*self.barMaxHeight)/maxdata
            c.addRect(-self.fontMargin, y,
                self.fontMargin, self.axisWidth)
            c.setColorV(self.labelColor)
            c.rightJustifyText(-self.fontMargin, y-self.tickShift, self.tickFormat%mark)
            mark += self.axisDelta
        return c

__middleware__ = BarChart

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
    axisDelta = 10
    D = {}
    D["labelsAndData"] = format(labelsAndData)
    D["axisDelta"] = format(axisDelta)
    D["barColor"] = format((0,0,0))
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
    app = BarChart()
    sresult = app(env, misc.ignore)
    result = "".join(list(sresult))
    print "test got", repr(result)
    if DUMPFILEPATH:
        print "written to", DUMPFILEPATH

if __name__=="__main__":
    test()
