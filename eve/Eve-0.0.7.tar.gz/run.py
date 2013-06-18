# -*- coding: utf-8 -*-

from eve import Eve
from eve.io.mongo import Validator
from eve.auth import BasicAuth, TokenAuth, HMACAuth
from hashlib import sha1
import hmac
from flask import request
from redis import Redis

redis = Redis()


class TAuth(TokenAuth):
    def check_auth(self, token, allowed_roles, resource):
        print token, resource
        return token == 'token'

class Auth(BasicAuth):
    def check_auth(self, username, password, allowed_roles, resource):
        print "resource:",resource
        return username == 'token'
        #return username == 'admin' and password == 'secret'


class Validator(Validator):
    def _validate_cin(self, cin, field, value):
        if cin:
            pass

def gotit(resource, request, response=None):

    print 'get', resource
    print request
    print response

def resource_gotit(request, response):
    print 'get_contacts'
    print request.data
    print response.data

def resource_post(request, response):
    print 'post_contacts'
    print request.authorization
    print request.form
    print response

def posting(resource, documents):
    print "posting to ", resource
    documents[0]["token"] = "mytoken"

def posting_r(documents):
    print "posting to resource contacts"


app = Eve(validator=Validator, auth=TAuth, redis=redis)
#app.config['DOMAIN']['contacts']['auth_username_field'] = 'name'
#app.on_get_contacts += resource_gotit
#app.on_get += gotit
#app.on_post_contacts += resource_post
#app.on_posting += posting
app.on_posting_contacts += posting_r

if __name__ == '__main__':
    #app.events.on_getting += pre
    #app.events.on_get += post
    app.run(debug=True)
