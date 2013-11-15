#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

""" how to use formv with webob """

import os, logging, formv
from mimetypes import guess_type, add_type
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

add_type('text/csv', '.csv', False)

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
formv.config = build(config_root=os.path.join(app_root, 'tests'))

class Application(object):
    def __call__(self, environ, start_response):
        self.request = Request(make_environ()) # - use prepared environ 
        response = self.request.get_response(self.response())
        return response(self.request.environ, start_response)
    
    def response(self):
        body = '<style>td { font: 11px sans-serif; }</style>'
        
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
        form = WebForm(allow_missing_keys=True,
                       allow_extra_keys=True,
                       replace_missing_key=True,
                       missing_key_value='dummy')    
        return form.validate(request)
            
application = Application()   


class WebForm(VSchema):
    """ form validator """
    
    fields = {        
        'first_name': VString(min_len=3, max_len=50),
        'last_name': VString(min_len=3, max_len=50),
        'email': VEmail(required=True),
        'address':VString(),
        'postcode_start': VString(),
        'postcode_end': VString(),
        'state': VString(),
        'country': VCountry(required=True, mode='by-name'),
        'currency': VString(),
        'price': VFloat(),
        'units': VInteger(),
        'pay_method': VString(),
        'phone': VString(),
        'phone_type': VString(),
        'fax': VString(),
        'date': VPipe(VToDate(date_format='%d/%m/%Y'), VDate(today_or_after=False)),
        'missing_field': VString(),
        'username': VString(),
        'password': VPassword(special_chars=3),     
        'file_pdf': VUploadFile(required=True),
        'file_jpg': VPipe(VUploadFile(), 
                          VWatermarkImage(text='watermark'),
                          VImprintImage(text='imprint')),
        'file_csv': VUploadFile(),
        'file_empty': VUploadFile(),
    }
    
    chains = {
        'contact': VAnyField(fields=('email', 'phone', 'fax'),
                             msg='Please provide some relevant, public contact details'), 
              
        'state': VState(country_field='country', 
                        state_field='state', mode='by-name'),

        'currency': VCurrency(country_field='country', 
                              currency_field='currency', mode='by-name'),

        'origin': VCountryPostcode(country_field='country', 
                                   postcode_field='postcode_start'),
        
        'destination': VCountryPostcode(country_field='country', 
                                        postcode_field='postcode_end'),
              
        'phone_type': VPair(required_field='phone_type',
                            required_label='Phone type', 
                            available_field='phone'),

        'pay_method': VPair(required_field='pay_method',
                            required_label='Payment method', 
                            available_field='price'), 
              
        'password': VEncodedPair(required_field='password',
                                 required_label='VPassword', 
                                 available_field='username'),

        'z-geodist': VGeoDistance(origin_field='origin', 
                                  destination_field='destination'),
    }
     

def make_environ():
    """ simulates a POST request (multipart/form-data) """
    
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_files_dir = os.path.join(app_root, 'tests/files')    
    fields = []

    # - plain fields
    fields.append(multipart.field('first_name', 'John'))
    fields.append(multipart.field('last_name', 'Smith'))
    fields.append(multipart.field('email', 'dummy@dummy.com'))
    fields.append(multipart.field('address', 'street & no.'))
    fields.append(multipart.field('postcode_start', '99501'))
    fields.append(multipart.field('postcode_end', '78081'))    
    fields.append(multipart.field('state', 'Alaska'))
    fields.append(multipart.field('country', 'U.S.A.'))
    fields.append(multipart.field('currency', '$'))
    fields.append(multipart.field('price', '500'))
    fields.append(multipart.field('units', '3'))
    fields.append(multipart.field('pay_method', 'cash'))
    fields.append(multipart.field('phone', '+1 234 56789'))
    fields.append(multipart.field('phone_type', 'mobile'))
    fields.append(multipart.field('fax', '+1 234 56789'))
    fields.append(multipart.field('date', '08/11/2012'))
    fields.append(multipart.field('username', 'dummy-username'))
    fields.append(multipart.field('password', 'dummy-secret-password-1'))
    
    # - file upload
    f = os.path.join(test_files_dir, 'test.pdf')
    fields.append(multipart.file('file_pdf', filename=f, 
                                 content_type=guess_type(f, False)[0]))            
    f = os.path.join(test_files_dir, 'test.jpg')
    fields.append(multipart.file('file_jpg', filename=f, 
                                 content_type=guess_type(f, False)[0]))            
    f = os.path.join(test_files_dir, 'test.csv')
    fields.append(multipart.file('file_csv', filename=f, 
                                 content_type=guess_type(f, False)[0]))            
    return env(*fields)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server   
    httpd = make_server('127.0.0.1', 9000, application)
    sn = httpd.socket.getsockname()
    print("Serving HTTP on", sn[0], "port", sn[1], "...")            
    httpd.serve_forever()

        
        
        
