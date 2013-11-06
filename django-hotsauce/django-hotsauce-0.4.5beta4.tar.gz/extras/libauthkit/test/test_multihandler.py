import sys
import os
from sample_app import TestApp 

def test_intercept(content_type='text/plain; charset=utf8'):
    # XXX Note, these tests don't test when the inclusion of a username and only test form
    # should also test all the other methods too for correct behaviour
    def sample_app(environ, start_response):
        if environ.get('PATH_INFO') == '/403':
            start_response('403 Forbidden', [('Content-type', content_type)])
            return ['Access denied']
        elif environ.get('PATH_INFO') == '/401':
            start_response('401 Unauthorized', [('Content-type', content_type)])
            return ['Not Authenticated']
        elif environ.get('PATH_INFO') == '/702':
            start_response('702 Doesnt exist', [('Content-type', content_type)])
            return ['Access denied']
        elif environ.get('PATH_INFO') == '/500':
            start_response('500 Error', [('Content-type', content_type)])
            return ['Internal Server Error']

    app = middleware(
        sample_app,
        setup_method=['digest'],
        digest_realm='test',
        digest_authenticate_user_data = """
            Username1:password1
            username2:password2
        """,
        cookie_signoutpath = '/signout',
        setup_intercept = "401, 403, 702",
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
    assertEqual(res.header('content-type'), 'text/plain; charset=utf8')
    assertEqual(res.full_status, '500 Error')
    assert 'Internal Server Error' in res
    
    res = TestApp(app).get('/401', status=401)
    assertEqual(res.header('content-type'), 'text/plain; charset=utf8')
    assertEqual(res.full_status, '401 Unauth')
    assert 'Not Authenticated' in res
    
def test_fail():
    for app in [basic_app, digest_app, config_app]:
        res = TestApp(app).get('/private', status=401)
        assertEqual(res.header('content-type'),'text/plain; charset=utf8')
        assertEqual(res.full_status, '401 Unauthorized')
        #raise Exception(res)
        print res
        assert 'This server could not verify that you are' in res

#def test_form_fail():
#    res = TestApp(form_app).get('/private', status=200)
#    assertEqual(res.header('content-type'),'text/plain; charset=UTF-8')
#    assertEqual(res.full_status, '200 OK')
#    assert 'Please Sign In' in res

def test_forward_fail():
    res = TestApp(forward_app).get('/private')
    assertEqual(res.header('content-type'),'text/plain; charset=utf8')
    # XXX Not sure about this but using a 401 triggers an infinite loop
    # of redirects.
    assertEqual(res.full_status, '200 Sign in required')
    #assert 'Please Sign In' in res

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
