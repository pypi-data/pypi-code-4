"""
Simple validator example which checks whether a cgi-argument
is within a numeric range
"""

skipWhiffDoc = "I'm not sure this one is a keeper"

# import must be absolute
from whiff.middleware import Validate
from whiff.middleware import misc
from whiff import whiffenv
from whiff import resolver

class NumericRange(Validate.Check):
    def __init__(self,
                 cgiVariable, # cgi variable to check
                 minValue=None, # minimum value
                 maxValue=None, # maximum value
                 envMessageKey="whiff.middleware.RangeError"
                 ):
        if minValue is None and maxValue is None:
            raise ValueError, "must specify one of minValue or maxValue"
        self.cgiVariable = cgiVariable
        self.minValue = minValue
        self.maxValue = maxValue
        self.envMessageKey = envMessageKey
    def convert(self, value, env):
        if value is None:
            return None
        return float(value)
    def validate(self, env):
        env = resolver.process_cgi(env, parse_cgi=True)
        minValue = self.param_value(self.minValue, env)
        maxValue = self.param_value(self.maxValue, env)
        minValue = self.convert(minValue, env)
        maxValue = self.convert(maxValue, env)
        #pr "numeric range", (minValue, maxValue)
        if maxValue is not None and minValue is not None and maxValue<minValue:
            raise ValueError, "max value is smaller than min value "+repr((maxValue, minValue))
        envMessageKey = self.param_value(self.envMessageKey, env)
        cgiVariable = self.param_value(self.cgiVariable, env).strip()
        cgi_parameters = env[whiffenv.CGI_DICTIONARY]
        success = True
        failure = False
        result = success # assumption
        message = None
        cgi_parameterList = cgi_parameters.get(cgiVariable)
        if cgi_parameterList is None:
            #pr "no require"
            result = failure
            message = None # no message if require is not set
        elif len(cgi_parameterList)!=1:
            #pr "too many parameters"
            result = failure
            message = "more than one value is not permitted"
        else:
            cgi_require = cgi_parameterList[0]
            #pr "require=", cgi_require
            try:
                cgi_value = self.convert(cgi_require, env)
            except ValueError:
                #pr "could not parse", cgi_require
                result = failure
                message = "could not parse value"
            else:
                if minValue is not None:
                    if cgi_value<minValue:
                        #pr "too small", cgi_value
                        result = failure
                        message = "value must be larger or equal to "+repr(minValue)
                if maxValue is not None:
                    if cgi_value>maxValue:
                        #pr "too large", cgi_value
                        result = failure
                        message = "value must be less or equal to "+repr(maxValue)
        #if message:
            ##pr "setting", (envMessageKey, message)
            #env[envMessageKey] = message
        return (result, envMessageKey, message)

__middleware__ = NumericRange

def test():
    env = {
        "wsgi.url_scheme" : "http",
        "PATH_INFO" : "/whatever",
        "QUERY_STRING" : "TESTVAR=1",
        "REMOTE_ADDR" : "127.0.0.1",
        "REMOTE_HOST" : "localhost",
        "REQUEST_METHOD" : "GET",
        "SCRIPT_NAME" : "",
        "SERVER_NAME" : "localhost",
        "SERVER_PORT" : "8888",
        "SERVER_PROTOCOL" : "HTTP/1.1",
        "SERVER_SOFTWARE" : "WSGIServer/0.1 Python/2.5",
        }
    r = NumericRange("TESTVAR", "0", "100")
    v = Validate.__middleware__("WRONG PAGE", r, "right page")
    sresult = v(env, misc.ignore)
    result = "".join(list(sresult))
    print "numeric range test results"
    print result
    r = NumericRange("TESTVAR", "5", "100")
    v = Validate.__middleware__("right page", r, "WRONG PAGE")
    sresult = v(env, misc.ignore)
    result = "".join(list(sresult))
    print result

if __name__=="__main__":
    test()
