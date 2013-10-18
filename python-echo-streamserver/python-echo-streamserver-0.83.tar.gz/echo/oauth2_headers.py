""" OAuth2 Authorization Headers

2-legged OAuth

The 2-legged OAuth uses the HMAC-SHA1 signature method, and the ACCESS key and SECRET.
This becomes the OAuth2 HTTP Authorization Headers (rather than Basic Authorization).
These HTTP headers are added to a urllib2.Request object before opening it.

The request must contain the following parameters as HTTP headers.
    oauth_consumer_key
    oauth_nonce
    oauth_timestamp
    oauth_version
    oauth_signature_method: Supported signature is HMAC-SHA1
    oauth_signature

The real request parameters must also be part of the signed OAuth2 headers.
    HTTP GET requires nothing, since the URL's query string alread has them.
    HTTP POST must also add the POST parameters to the OAuth parameters list.

"""
# python-oauth2 may not be available, and a stub function is provided.
try:
    import oauth2, time

    ECHO_OAUTH2=True
    def get_oauth2_headers(access_key, secret_key, url, method, post_params=None):
        params = {
            'oauth_version': "1.0",
            'oauth_nonce': oauth2.generate_nonce(),
            'oauth_timestamp': int(time.time()),
        }
        consumer = oauth2.Consumer(key=access_key, secret=secret_key)
        params['oauth_consumer_key'] = consumer.key
        # Combine OAuth2 params with the HTTP POST ones, when given.
        if post_params:
            params.update(post_params)
        request = oauth2.Request(method=method, url=url, parameters=params)
        signature_method = oauth2.SignatureMethod_HMAC_SHA1()
        request.sign_request(signature_method, consumer, None)
        return request.to_header()
except ImportError:
    ECHO_OAUTH2=False
    def get_oauth2_headers(access_key, secret_key, url, method, post_params=None):
        return {} # empty header dict.

if __name__ == "__main__":
    import urllib, urllib2

    ACCESS=''
    SECRET=''
    SAMPLE_URL=''
    SAMPLE_METHOD='GET'
    SAMPLE_DATA={}

    # Oauth2 Signed urllib2.Request:
    try:
        request = urllib2.Request(SAMPLE_URL)
        if 'GET' == SAMPLE_METHOD:
            request.headers = get_oauth2_headers(ACCESS, SECRET, SAMPLE_URL, SAMPLE_METHOD)
            connection = urllib2.urlopen(request)
        else: # 'POST'
            request.headers = get_oauth2_headers(ACCESS, SECRET, SAMPLE_URL, SAMPLE_METHOD, SAMPLE_DATA)
            connection = urllib2.urlopen(request, urllib.urlencode(SAMPLE_DATA))
        data = connection.read()
        print data
    except urllib2.HTTPError, e:
        print "HTTP: %r\n%r" % (e.code, e.read())

