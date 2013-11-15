#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

""" how to validate a credit card """

import os, logging, formv
from webob import Request, Response

from formv.configuration import build
from formv.validators import *
from formv.exception import Invalid

from formv.utils.compat import PY2
from tests import multipart
from examples import to_str, make_environ as env

logging.basicConfig(filename='../logs/formv.log', level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s][%(filename)s] %(message)s %(name)s %(funcName)s (line: %(lineno)d)')
log = logging.getLogger(__name__)

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
formv.config = build(config_root=os.path.join(app_root, 'tests'))

class Application(object):
    def __call__(self, environ, start_response):
        self.request = Request(make_environ()) # - use prepared environ 
        response = self.request.get_response(self.response())
        return response(self.request.environ, start_response)
    
    def response(self):
        body = ''
        
        try:
            form = self.validate(self.request.POST) # - form validation
            body += '<b>success</b>'
            body += to_str(form)
        except Invalid as e:
            body += e.message
            body += '<br/>errors'
            body += to_str(e.errors)
            body += '<br/>values'
            body += to_str(e.value)

        response = Response()                        
        response.text = unicode(body) if PY2 else body
        return response
        
    def validate(self, request):
        form = WebForm(remove_empty_keys=True)    
        return form.validate(request)
            
application = Application()   


class WebForm(VSchema):
    """ form validator """
    
    fields = {        
        'card_type': VString(required=True),
        'card_number': VString(required=True),
        'card_expiration': VString(required=True),
        'card_security_code':VString(required=True),
    }
    
    chains = {
        None: VCreditCard(card_type_field='card_type', 
                          card_number_field='card_number', 
                          card_expiration_field='card_expiration', 
                          card_security_code_field='card_security_code'), 
    }
     

def make_environ():
    """ simulates a POST request (multipart/form-data) """   
    return env(multipart.field('card_type', 'VISA'),
               multipart.field('card_number', '4012888888881881'),
               multipart.field('card_expiration', '10/2018'),
               multipart.field('card_security_code', '432'))


if __name__ == '__main__':
    from wsgiref.simple_server import make_server   
    httpd = make_server('127.0.0.1', 9000, application)
    sn = httpd.socket.getsockname()
    print("Serving HTTP on", sn[0], "port", sn[1], "...")            
    httpd.serve_forever()

        
        
        
