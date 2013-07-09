"""
Generate a link which evaluates to a bar chart
"""

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/png/barChartLink - link to bar chart
{{/include}}

The <code>whiff_middleware/png/barChartLink</code>
middleware generates a link which evaluates to a bar chart.

{{include "example"}}
{{using targetName}}barChartLink{{/using}}
{{using page}}

<img src="{{include "whiff_middleware/png/barChartLink"}}
    {{using labelsAndData}}
        [
        ["december", 30],
        ["january", 50],
        ["february", 40],
        ["march", 15],
        ["april", 64],
        ["may", 4],
        ["june", 49],
        ["july", 37]
        ]
    {{/using}}
    {{using axisDelta}}
        10
    {{/using}}
{{/include}}">

{{/using}}
{{/include}}

"""

# import must be absolute
from whiff.middleware import GetPageLink
from whiff.middleware import misc
from whiff.middleware.png import barChart
from whiff.rdjson import jsonParse

class barChartLink(misc.utility):
    def __init__(self, labelsAndData, axisDelta, **other_parameters):
        if other_parameters.has_key("page"):
            raise ValueError, "page require not allowed"
        for k in other_parameters.keys():
            if not hasattr(barChart.BarChartBase, k):
                raise ValueError, "unknown require "+repr(k)
        self.labelsAndData = labelsAndData
        self.axisDelta = axisDelta
        self.other_parameters = other_parameters
    def __call__(self, env, start_response):
        #pr "calling barChartLink"
        labelsAndData = self.param_json(self.labelsAndData, env)
        labelsAndData = jsonParse.formatIfNotString(labelsAndData)
        #pr "formatted ld", labelsAndData
        axisDelta = self.param_json(self.axisDelta, env)
        axisDelta = jsonParse.formatIfNotString(axisDelta)
        params = {}
        for (k,v) in self.other_parameters.items():
            v = self.param_json(v, env)
            fv = jsonParse.formatIfNotString(v)
            params[k] = fv
        #pr "from", self.other_parameters
        #pr "sending", params
        page = '{{include "whiff_middleware/png/barChart"/}}'
        self.app =  GetPageLink.__middleware__(page=page,
                                          labelsAndData=labelsAndData,
                                          axisDelta=axisDelta, **params)
        return self.app(env, start_response)

__middleware__ = barChartLink

def test():
    env = {
        "wsgi.url_scheme" : "http",
        "PATH_INFO" : "/whatever",
        "QUERY_STRING" : "",
        "REMOTE_ADDR" : "127.0.0.1",
        "REMOTE_HOST" : "localhost",
        "REQUEST_METHOD" : "GET",
        "SCRIPT_NAME" : "",
        "SERVER_NAME" : "localhost",
        "SERVER_PORT" : "8888",
        "SERVER_PROTOCOL" : "HTTP/1.1",
        "SERVER_SOFTWARE" : "WSGIServer/0.1 Python/2.5",
        }
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
    testapp = barChartLink(labelsAndData, axisDelta, barColor=(55,55,55))
    print "test link output"
    result = "".join(list(testapp(env, misc.ignore)))
    print len(result)
    print repr(result)

if __name__=="__main__":
    test()
    

