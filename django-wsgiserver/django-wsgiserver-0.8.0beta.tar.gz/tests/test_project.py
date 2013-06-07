# This is still a skelton right now
# 1. assume that all requirements are met currently
# 2. ? manipulate PYTHONPATH?
# 3. spawn python testdjangoproject/testdjango/manage.py runwsgiserver [options]
# 4. run test appropriate
# 5. repeat 3 + 4 with appropriate options



# using requests with django
# probably useful for api testing
# command line clients
# requests is not the highest efficiency library---eventually might need curl-based system
# if trying to do high volume application

# for django I'm using the following strategy for dealing with csrf security
# the main index includes the token. I then save this and use it in following requests
# by sending 'X-CSRFToken': csrftoken in the following headers
# I added this to my template in django to force the appearance of the csrf cookie
#  <div style="display:none"> <-- force inclusion of the cookie -->
#    <input type="hidden" name="csrfmiddlewaretoken" value="{{csrf_token}}"/>
#  </div>
# my view uses RequestContext to render the template

import requests, sys, os, time
import subprocess

PIDFILE = os.path.join(os.getcwd(),'test_project.pid')

def launch_project():
    """start django wsgiserver as daemon"""
    print "hello from launch project"
    subprocess.call(["python", r"testdjangoproject/testdjango/manage.py", "runwsgiserver",
                     "threads=10", "daemonize", "pidfile=%s" % PIDFILE])
    return None

def stop_project():
    print "hello from stop project"
    subprocess.call(["python", r"testdjangoproject/testdjango/manage.py", "runwsgiserver", "stop", "pidfile=%s" % PIDFILE])
    return None
    


def do_tests():
    session = requests.Session()
    r = session.get(r'http://localhost:8000/') # a session allows for persistent cookies and things

    # print "cookies:", r.cookies
    csrftoken = r.cookies['csrftoken'] # or something
    # print "csrftoken:", csrftoken, 

    # xmlrequestheader 
    # sys.exit(0)
    # test ajax
    # import json
    # useragent = 'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)'


    payload = {'some':'data'}

    headers= {#'content-type':'application/json',
              'X-CSRFToken': csrftoken }


    def check(resp):
        # print resp.status_code,
        if resp.status_code==200:
            print 'OK [%s] %s %s' % (resp.request.method, resp.request.path_url, resp.status_code)
        else:
            print 'BAD [%s] %s %s' % (resp.request.method, resp.request.path_url, resp.status_code)
        return resp

    staticfilename = 'teststaticfile1.txt'
    r = check(session.get(os.path.join(r'http://localhost:8000/static/',staticfilename)))

    # print "static file:", r.text, repr(r.text), repr(staticfilename)

    url = r'http://localhost:8000/testajax/' # remember it needs to end in a slash

    check(session.get(url, headers=headers))
    check(session.post(url, data='', headers=headers))
    check(session.put(url, data='', headers=headers))
    check(session.delete(url, data='', headers=headers))
    check(session.head(url, data='', headers=headers))
    check(session.options(url, data='', headers=headers))
    check(session.patch(url, data='', headers=headers))


# payload = {'key1': 'value1', 'key2': 'value2'}
# r = requests.post("http://httpbin.org/post", data=payload)
# print r.text

##### test autoload ####

if __name__== '__main__':
    try:    
        launch_project()
        print "started project"
        time.sleep(1.0)
        do_tests()
        raw = raw_input("press to end")
        stop_project()
    except: # KeyboardInterrupt:
        stop_project()




