
"""
Validate data in environment using a check page
"""

skipWhiffDoc = "I'm not sure this one is a keeper"

# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv
from whiff import resolver
from whiff.rdjson import jsonParse

class Validate(misc.utility):
    """
    checks return json values (success, varname, message) where success is true or false
    and message if not null is an error message string. and varname is a variable to store
    the message in the environment.
    """
    def __init__(self,
                 pageToCheck,   # page to validate (return here if not valid)
                 check,  # check page (sequence),
                         # returns "true" or "false" and possibly modifies environment (parsing cgi, adding error message, etc)
                 successPage, # page to go to when the validation passes
                 ):
        self.pageToCheck = pageToCheck
        self.check = check
        self.successPage = successPage
    def __call__(self, env, start_response):
        checks = self.param_value(self.check, env)
        #pr "Validate got", repr(checks)
        valid = True
        # look for any failure in possibly multiple check returns
        cursor = 0
        lenchecks = len(checks)
        while cursor<lenchecks:
            (flag, jsonResult, endLocation) = jsonParse.parseValue(checks, cursor)
            if not flag:
                raise ValueError, "could not parse check results: "+repr(jsonResult)
            cursor = endLocation
            (valid1, varname, message1) = jsonResult
            if message1:
                env[varname] = message1
            if not valid1:
                valid = False
        if valid:
            return self.deliver_page(self.successPage, env, start_response)
        else:
            return self.deliver_page(self.pageToCheck, env, start_response)

class Check(misc.utility):
    "utility superclass for making check middlewares"
    def validate(self, env):
        raise ValueError, "abstract method must be defined at subclass"
    def __call__(self, env, start_response):
        (valid, messageKey, message) = self.validate(env)
        payload = (valid, messageKey, message)
        jsonpayload = jsonParse.format(payload)
        start_response("200 OK", [('Content-Type', 'text/plain')])
        #pr "result", jsonpayload
        return [jsonpayload]

__middleware__ = Validate

# tested by Range

