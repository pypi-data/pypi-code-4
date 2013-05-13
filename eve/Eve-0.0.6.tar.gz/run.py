# -*- coding: utf-8 -*-

from eve import Eve
from eve.io.mongo import Validator
from eve.auth import BasicAuth, TokenAuth, HMACAuth
from hashlib import sha1
import hmac
from flask import request


class Auth(BasicAuth):
    def check_auth(self, username, password, allowed_roles):
        return username == 'admin' and password == 'secret'


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
    print request
    print response

app = Eve(validator=Validator)
#app.config['DOMAIN']['contacts']['auth_username_field'] = 'name'
#app.on_get_contacts += resource_gotit
#app.on_get += gotit
#app.on_post_contacts += resource_post

if __name__ == '__main__':
    #app.events.on_getting += pre
    #app.events.on_get += post
    app.run(debug=True)
