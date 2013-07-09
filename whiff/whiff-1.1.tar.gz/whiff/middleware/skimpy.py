
"""
Very simple captcha implementation using a secret value
and a session variable.

Get a time value from a cookie.  If the time has not expired
hash the time together with the secret and generate a numeric
value from the hash.  Use the numeric value for comparing
with user input and for generating captcha image.

This middleware uses whiff session resources.
"""

whiffCategory = "tools"

whiffDoc = """
{{include "whiff_middleware/heading"}}
whiff_middleware/skimpy - a CAPTCHA protocol middleware
{{/include}}

The <code>whiff_middleware/skimpy</code>
middleware implements a simple CAPTCHA using
cookies and WHIFF session resources.
This middleware will only work correctly if
<code>skimpyGimpy</code> is installed separately.
The <code>skimpyGimpy</code> package is not
installed automatically.

"""
MESSAGEKEY = "whiff.middleware.skimpy.Message"

from skimpyGimpy import skimpyAPI # this middleware requires skimpyGimpy
import hashlib
import time
import Cookie
import sys

# import must be absolute
from whiff.middleware import misc
from whiff import whiffenv
from whiff import resolver
from whiff import gateway

def numeric_hash(v, secret, minimum=5000):
    "repeatably make up an arbitrary number based on the input values, larger than minimum"
    m = hashlib.md5()
    m.update(repr(v)+repr(secret))
    d = m.digest()
    result = 0
    count = 0
    while result<minimum:
        result = result*7
        result = result+((ord(d[count])+count)%11)
        count+=1
        if count>len(d):
            return result+175+minimum
    return result

defaultTimeOut = 100
defaultSecret = "default secret "+str(sys.version)+str(time.time())

class skimpyCaptchaCheck(misc.utility):
    def __init__(self,
                 captchapage, # the page to hold the captcha
                 successpage, # page to present on success
                 variable="number", # cgi variable to hold the incoming value
                 imgflag="image", # cgi variable requesting an image
                 secretPath=["captchaSecret"], # resource path to string secret for generating hash, should generate a new secret every access
                 captchaPath=["session", "item", "captcha"], # resource path for archiving captcha value
                 timeoutPath=["captchaTimeOut"], # number of seconds captcha is valid
                 cookiename="skimpycookie", # name to use for time cookie
                 ):
        self.captchapage = captchapage
        self.successpage = successpage
        self.variable = variable
        self.imgflag = imgflag
        self.secretPath = secretPath
        self.captchaPath = captchaPath
        self.timeoutPath = timeoutPath
        self.cookiename = cookiename
        #pr "skimpy check inited"
        #pr "(self.variable, self.imgflag, self.timeout, self.cookiename)"
        #pr (self.variable, self.imgflag, self.timeout, self.cookiename)
    def skimpy_start_response_function(self, start_response, cookiename, cookievalue):
        if not cookievalue:
            return start_response
        def result(status, headers):
            cookietext = "%s=%s; path=/" % (cookiename, cookievalue)
            #pr "setting cookie", cookietext
            my_headers = headers + [ ('Set-Cookie', cookietext) ]
            return start_response(status, my_headers)
        return result
    def __call__(self, env, start_response):
        #pr; #pr "skimpy entered at", time.time()
        secretPath = self.param_json(self.secretPath, env)
        variable = self.param_value(self.variable, env)
        variable = resolver.local_cgi_name(variable, env)
        imgflag = self.param_value(self.imgflag, env)
        timeoutPath = self.param_json(self.timeoutPath, env)
        cookiename = self.param_value(self.cookiename, env)
        captchaPath = self.param_json(self.captchaPath, env)
        # find the resources
        try:
            captcha = gateway.getResource(env, captchaPath)
        except gateway.UnknownResource:
            captcha = None
        try:
            timeout = gateway.getResource(env, timeoutPath)
        except gateway.UnknownResource:
            timeout = defaultTimeOut
        timeout = float(timeout)
        try:
            secret = gateway.getResource(env, secretPath)
        except gateway.UnknownResource:
            secret = defaultSecret
        message = None
        #pr "got captcha, timeout, secret", (captcha, timeout, secret)
        # parse both get and post parameters
        env = resolver.process_cgi(env, parse_cgi=True)
        cgi_parameters = env[whiffenv.CGI_DICTIONARY]
        #pr "parameters are", cgi_parameters
        # otherwise decide whether to emit success or captcha form...
        # find the cookie value and check that it hasn't timed out, set a new one if so
        cookie_header = env.get("HTTP_COOKIE")
        cookievalue = None # assume it's not there...
        if cookie_header is not None:
            c = Cookie.SimpleCookie(cookie_header)
            if c.has_key(cookiename):
                cookievalue = c[cookiename].value
                #pr "found cookievalue", repr(cookievalue)
                try:
                    cookietime = float(cookievalue)
                except ValueError:
                    #pr "could not parse cookie as float", repr(cookievalue)
                    cookievalue = None # bad data
                else:
                    # timed out?
                    elapsed = time.time()-cookietime
                    if elapsed>timeout:
                        #pr "timed out", cookievalue
                        cookievalue = None # timed out
                        if cgi_parameters.get(variable)!=None:
                            message = "captcha time limit expired"
        # if the cookievalue is not known or timed out assign a new one
        if cookievalue is None:
            cookievalue = str(time.time())
        else:
            # otherwise use the existing cookie value
            #pr "valid cookie found", repr(cookievalue)
            pass
        # if the request is for an image, deliver captcha image
        if cgi_parameters.get(imgflag)!=None:
            # set the captcha resource
            captcha = str( numeric_hash((time.time(), cookievalue), secret) )
            #pr "setting captcha", captcha
            gateway.putResource(env, captchaPath, captcha)
            #pr "delivering image", captcha
            speckle = 0.3
            scale = 2.1
            my_start_response = self.skimpy_start_response_function(start_response, cookiename, cookievalue)
            gen = skimpyAPI.Png(captcha, speckle=speckle, scale=scale)
            imagedata = gen.data()
            my_start_response("200 OK", [('Content-Type', 'image/png')])
            return [imagedata]
        # otherwise if there is a variable value and it matches the hashed cookie, deliver successpage
        if cookievalue is not None:
            inputvalues = cgi_parameters.get(variable)
            if inputvalues is not None and len(inputvalues)==1:
                inputvalue = inputvalues[0].strip()
                hashvalue = captcha
                hashstring = str(hashvalue)
                #pr "comparing", (inputvalue, hashstring)
                if inputvalue==hashstring:
                    # success!
                    # invalidate the cookie
                    cookievalue = "XXX"+str(numeric_hash(captcha, captcha))
                    my_start_response = self.skimpy_start_response_function(start_response, cookiename, cookievalue)
                    #pr "skimpy test passed: delivering success page"
                    return self.deliver_page(self.successpage, env, my_start_response)
                else:
                    message = "input did not match generated image"
            else:
                message = "no captcha input found"
        # otherwise deliver captchapage and make a new cookie value
        #pr "skimpy test failed, delivering captchapage"
        if message:
            env[MESSAGEKEY] = message
        cookievalue = str(time.time())
        my_start_response = self.skimpy_start_response_function(start_response, cookiename, cookievalue)
        return self.deliver_page(self.captchapage, env, my_start_response)

__middleware__ = skimpyCaptchaCheck

def img_test_DOESNT_WORK(imgpath="/tmp/test.png"):
    "IMAGE GENERATION ONLY WORKS WHEN SESSION RESOURCES ARE AVAILABLE"
    env = {
        "wsgi.url_scheme" : "http",
        "PATH_INFO" : "/whatever",
        "QUERY_STRING" : "image=1",
        "REMOTE_ADDR" : "127.0.0.1",
        "REMOTE_HOST" : "localhost",
        "REQUEST_METHOD" : "GET",
        "SCRIPT_NAME" : "",
        "SERVER_NAME" : "localhost",
        "SERVER_PORT" : "8888",
        "SERVER_PROTOCOL" : "HTTP/1.1",
        "SERVER_SOFTWARE" : "WSGIServer/0.1 Python/2.5",
        }
    imageapp = skimpyCaptchaCheck("", "", "secret")
    def start_response(status, headers):
        print "testing: start_response called"
        print "status = ", status
        print "headers = ", headers
    sresult = imageapp(env, start_response)
    lresult = list(sresult)
    result = "".join(lresult)
    print "got", len(result), "bytes; writing to", imgpath
    open(imgpath, "wb").write(result)
    print "done with image test"
    print

def txt_test():
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
    textapp = skimpyCaptchaCheck("This should be a page with a skimpy form in it",
                                 "WRONG PAGE", "secret")
    def start_response(status, headers):
        print "start_response called"
        print "status = ", status
        print "headers = ", headers
    sresult = textapp(env, start_response)
    lresult = list(sresult)
    result = "".join(lresult)
    print "got", len(result), "bytes"
    print "TEXT"
    print result
    print "END OF TEXT"
    

if __name__=="__main__":
    #img_test()
    txt_test()
