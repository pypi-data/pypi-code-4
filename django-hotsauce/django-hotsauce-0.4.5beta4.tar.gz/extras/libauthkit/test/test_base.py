# Very basic tests which so no more than check each of the authentication
# methods to ensure that an unprotected page is accessible and that a 
# protected page triggers the a sign in.
# 
# Note: Should the Form and Forward methods return 401 or 200 when they
# generate an HTML page for the user to sign in?

import sys, os

from authkit.authenticate import middleware
from authkit.middleware import lint as lint_app

# middlewares
import authkit.authenticate.form    as form_app
import authkit.authenticate.basic   as basic_app
import authkit.authenticate.digest  as digest_app
import authkit.authenticate.forward as forward_app
import authkit.authenticate.redirect as redirect_app
import authkit.authenticate.cookie   as cookie_app
#import authkit.authenticate.open_id as open_id

import sample_app

apps = [make_app(app) for app in (basic_app, digest_app, forward_app, redirect_app, cookie_app)]

def make_app(mod, callback):
    # Add the validation middleware
    print("processing module=%s"%mod)
    return lint_app.middleware(getattr(mod, 'app'))

def assertEqual(a,b):
    if a != b:
        raise AssertionError('%s != %s'%(a,b))

def assertAllEqual(*args):
    if not len(args)>2:
        raise Exception("Need two arguments")
    a = args[0]
    for b in args[1:]:
        if a != b:
            raise AssertionError('%s != %s'%(a,b))


def test_ok():
    for app in apps:
        if app.__name__ == 'forward':
            res = TestApp(app).get('')
            assertEqual(res.header('content-type'), 'text/plain')
            assertEqual(res.full_status, '200 OK')
            assert 'You Have Access To This Page.' in res
        else:
            res = TestApp(app).get('')
            assertEqual(res.header('content-type'), 'text/plain; charset=UTF-8')
            assertEqual(res.full_status, '200 OK')
            assert 'You Have Access To This Page.' in res
        del res

def test_intercept():
    # XXX Note, these tests don't test when the inclusion of a username and only test form
    # should also test all the other methods too for correct behaviour
    def sample_app(environ, start_response):
        if environ.get('PATH_INFO') == '/403':
            start_response('403 Forbidden', [('Content-type', 'text/plain')])
            return ['Access denied']
        elif environ.get('PATH_INFO') == '/401':
            start_response('401 Unauthorized', [('Content-type', 'text/plain')])
            return ['Not Authed']
        elif environ.get('PATH_INFO') == '/702':
            start_response('702 Doesnt exist', [('Content-type', 'text/plain')])
            return ['Access denied']
        elif environ.get('PATH_INFO') == '/500':
            start_response('500 Error', [('Content-type', 'text/plain')])
            return ['Error']

    app = middleware(
        sample_app,
        setup_method=['digest'],
        digest_realm='test',
        digest_authenticate_user_data = """
            Username1:password1
            username2:password2
        """,
        cookie_signoutpath = '/signout',
        setup_intercept = "403, 702",
    )
    res = TestApp(app).get('/403', status=401)
    assertEqual(res.header('content-type'), 'text/plain; charset=utf8')
    # XXX Should this keep the original status code or not?
    assertEqual(res.full_status, '401 Unauthorized')
    assert 'This server could not verify that you are authorized' in res

    res = TestApp(app).get('/702', status=401)
    assertEqual(res.header('content-type'), 'text/plain; charset=utf8')
    # XXX Should this keep the original status code or not?
    assertEqual(res.full_status, '401 Unauthorized')
    assert 'This server could not verify that you are authorized' in res

    res = TestApp(app).get('/500', status=500)
    assertEqual(res.header('content-type'), 'text/plain')
    assertEqual(res.full_status, '500 Error')
    assert 'Error' in res
    
    res = TestApp(app).get('/401', status=401)
    assertEqual(res.header('content-type'), 'text/plain')
    assertEqual(res.full_status, '401 Unauth')
    assert 'Not Authed' in res
    
def test_fail():
    for app in [basic_app, digest_app, config_app]:
        res = TestApp(app).get('/private', status=401)
        assertEqual(res.header('content-type'),'text/plain; charset=utf8')
        assertEqual(res.full_status, '401 Unauthorized')
        #raise Exception(res)
        assert 'This server could not verify that you are' in res

def test_form_fail():
    res = TestApp(form_app).get('/private', status=200)
    assertEqual(res.header('content-type'),'text/html; charset=UTF-8')
    assertEqual(res.full_status, '200 OK')
    assert 'Please Sign In' in res

def test_forward_fail():
    res = TestApp(forward_app).get('/private')
    assertEqual(res.header('content-type'),'text/html')
    # XXX Not sure about this but using a 401 triggers an infinite loop
    # of redirects.
    assertEqual(res.full_status, '200 Sign in required')
    assert 'Please Sign In' in res

#def test_openid_fail():
#    res = TestApp(openid_app).get('/private')
#    assertEqual(res.header('content-type'),'text/html; charset=UTF-8')
#    assertEqual(res.full_status, '200 OK')
#    assert 'Please Sign In' in res

def test_redirect_fail():
    res = TestApp(redirect_app).get('/private', status=302)
    assertEqual(res.header('Location'),'http://vigile.net')
    assertEqual(res.full_status, '302 Found')
#
