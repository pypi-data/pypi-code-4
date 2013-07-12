#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys,os
import time
import json
import urllib
import baker
import urllib2
import oauth2 as oauth

def client(consumer_key, consumer_secret, access_key, access_secret):
    """instantiate an oauth client"""
    consumer=oauth.Consumer(key=consumer_key, secret=consumer_secret)
    token=oauth.Token(access_key, access_secret)
    return oauth.Client(consumer, token)

suffix_to_parser=dict(
    json=json.loads,
)

def load_cred(cred_file):
    """load credential file --> {consumer_key, consumer_secret, access_key, access_secret}"""

    _,suffix=os.path.splitext(cred_file)

    try:
        parser=suffix_to_parser[suffix.lower().lstrip('.')]
    except KeyError:
        raise RuntimeError('unsupported format', suffix)

    # xx allow other fields by selecting the keys here
    return parser(file(cred_file).read())

def hdr_dict(content_type, extra_hdrs):
    """convert header args to a dict that client.request can take"""
    headers = dict([ (k.replace('_','-'), v) for k,v in extra_hdrs.items() ])
    headers['content-type']=content_type
    return headers

def select(selector, data):
    """select value from data
    simple dict key is supported for now.
    todo: use jsonpath or jq.
    """
    if selector in (None, '.'):
        return data
    return data.get(selector)

@baker.command
def oget(cred, url):
    """GET the url with oauth 
    ourl oget access_token.json https://api.twitter.com/1.1/users/lookup.json?screen_name=gvanrossum
    """
    c=client(**load_cred(cred))
    response, content = c.request(url, 'GET')
    print content

@baker.command
def get(url):
    """GET the url"""
    req=urllib2.Request(url)
    rsp=urllib2.urlopen(req)
    print rsp.read()

@baker.command
def opost(cred, url, 
          request_selector='.',
          response_selector='.',
          strict=False, 
          sleep=10,            # for niceness
          content_type='application/x-www-form-urlencoded', **extra_hdrs):
    """Oauth'ed POST
    POST json data read from stdin...

    input/output format and {request/response}_selector
    DOCUMENT_ME

    { request: { foo: bar } } --> { requset: { foo: bar}, # echoed request data.
                                    response_headers: {}, # header dict
                                    response:             # content of the reponse.
                                  }

    The input and output structured can be modified with request_selector and response_selector, 
    repectively.

    * request_selector: 
                If specified, it is used to extract the request data from 
                the input values. This option can be used to preserve the request 
                and passed down stream along with the response.
                echo '{request: {foo: bar} }' | posts --request_selector req -->
                      {request: {foo: bar}, response: {...} }

                If selector fails, the value is passed down as it.
                This allows for heterogenous stream, mixing requests and other data.

    In an unlikely event that extra_hdrs conflict with other args (strict, etc), 
    header/arg name can be prefixed with _.
    """
    sleep=int(sleep)
    c=client(**load_cred(cred))
    hdrs=hdr_dict(content_type, extra_hdrs)

    for data_json in sys.stdin.readlines():

        data_rep=data_json      # data representation for error reporting.
        try:
            data=json.loads(data_json)
            data_rep=data

            request_data=select(request_selector ,data)
            if request_data is None:
                # I am not to handle this. pass it thru..
                print data_json
                continue
            # optionally dump selected request_data for debugging..

            body=urllib.urlencode(request_data)
            response_hdrs, content = c.request(url, 'POST', body, hdrs)

            # inject response in the envelope and print.
            # helpfully decode content if json.
            if response_hdrs.get('content-type','').lower().startswith('application/json'):
                # parse out charset as well: application/json; charset=utf-8
                reponse_data=json.loads(content)
            else:
                reponse_data=content
            # 
            # form the output
            # 
            if response_selector=='.':
                # just dump the response without http info
                data=reponse_data
            else:
                # inject into the envelope
                data[response_selector]=reponse_data
                data['response_headers']=response_hdrs
            print json.dumps(data)

        except Exception, e:
            if strict:
                raise
            else:
                print json.dumps(['error', url, data_rep, repr(e)])
    
        if sleep:
            time.sleep(sleep)

# todo: posts. like above, but without oauth.

documentation="""

### usage

* GET
  $ ourl.py oget x.cred.json 'https://api.twitter.com/1.1/users/lookup.json?screen_name=gvanrossum'
  Essentially a curl that does oauth

* POST

    $ echo '{"screen_name": "gvanrossum"}' \
	| ourl.py opost access_token.json \
		'https://api.twitter.com/1.1/users/lookup.json' \
	| jq -M .

* access token
    $ cat access_token.json

    {
      "consumer_key": "XXXX",
      "consumer_secret": "XXXX",
      "access_key": "xxxx",
      "access_secret": "XXXX"
    }


### naming convention

* 'o' prefix indicates Oauth'ed interaction
  'oget' does oauth, while 'get' does a plain GET.

"""

@baker.command
def doc():
    """documentation"""
    print documentation

def main():

    baker.run()

if __name__=='__main__':

    main()
