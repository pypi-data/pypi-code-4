"""
Generate a link which evaluates to a pie chart
"""


whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/png/pieChartLink - link to pie chart
{{/include}}

The <code>whiff_middleware/png/pieChartLink</code>
middleware generates a link which evaluates to a pie chart.

{{include "example"}}
{{using targetName}}pieChartLink{{/using}}
{{using page}}

<img src="{{include "whiff_middleware/png/pieChartLink"}}
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
    {{using radius}}
        140
    {{/using}}
{{/include}}">

{{/using}}
{{/include}}

"""

# import must be absolute
from whiff.middleware import GetPageLink
from whiff.middleware import misc
from whiff.middleware.png import pieChart
from whiff.rdjson import jsonParse

class pieChartLink(misc.utility):
    def __init__(self, labelsAndData, radius, **other_parameters):
        if other_parameters.has_key("page"):
            raise ValueError, "page require not allowed"
        for k in other_parameters.keys():
            if not hasattr(pieChart.PieChartBase, k):
                raise ValueError, "unknown require "+repr(k)
        self.labelsAndData = labelsAndData
        self.radius = radius
        self.other_parameters = other_parameters
    def __call__(self, env, start_response):
        #pr "calling pieChartLink"
        labelsAndData = self.param_json(self.labelsAndData, env)
        labelsAndData = jsonParse.formatIfNotString(labelsAndData)
        #pr "formatted ld", labelsAndData
        radius = self.param_json(self.radius, env)
        radius = jsonParse.formatIfNotString(radius)
        params = {}
        for (k,v) in self.other_parameters.items():
            v = self.param_json(v, env)
            fv = jsonParse.formatIfNotString(v)
            params[k] = fv
        #pr "from", self.other_parameters
        #pr "sending", params
        page = '{{include "whiff_middleware/png/pieChart"/}}'
        self.app =  GetPageLink.__middleware__(page=page,
                                          labelsAndData=labelsAndData,
                                          radius=radius, **params)
        return self.app(env, start_response)

__middleware__ = pieChartLink

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
    radius = 150
    testapp = pieChartLink(labelsAndData, radius, labelColor=(55,55,55))
    print "test link output"
    result = "".join(list(testapp(env, misc.ignore)))
    print len(result)
    print repr(result)

if __name__=="__main__":
    test()
    

