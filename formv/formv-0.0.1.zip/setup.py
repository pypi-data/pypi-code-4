#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import sys
from setuptools import setup, find_packages

version = '0.0.1'

PY2 = sys.version_info[0] == 2
PY3 = sys.version_info[0] >= 3

def install_requires():
    if PY2:
        return ['pyyaml>=3.10', 'pycrypto>=2.6', 
                'PIL>=1.1.7', 'dnspython>=1.11.0']
    if PY3:
        return ['pyyaml>=3.10', 'pycrypto>=2.6', 
                'Pillow>=2.1.0', 'dnspython3>=1.11.0']

setup(name='formv',
      version=version,
      description="HTML forms validation, conversion & transformation",
      long_description="""\
*formv* is a configurable Python library that can be used to validate, 
convert & transform HTML forms. It was tested under Python 2.7 and 3.2.

Includes validators for::

  basic types 
     - boolean, strings, numbers, dates, time, ranges, lists, sets
  chained types 
     - pairs, multiple fields, post-codes, states, currencies, 
       languages, phone numbers, credit cards
  compound types 
     - any validator, piped validators
  signers & encoders 
     - cost-based PBKDF2 encoding used to sign strings (e.g. cookies) and 
       encode strings (e.g. user, password) and sign serialized objects 
       (e.g. session objects stored in cache/on disk)  
  documents 
     - can be validated (size, mime-type), stored, backed-up, compressed, 
       reused
  images 
     - can be validated (size, mime-type), stored, backed-up, resized, 
       watermarked, imprinted, reused
  geographic data 
    - based on extendable YAML configuration files or user-defined callables 
      (countries, country-codes, states, various naming styles, currencies, 
      languages, post-codes, latitude, longitude, geo-distance calculation)
  network related 
     - IPv4, IPv6, CIDR, MAC
  web-forms (schema validation)
      - simple fields, chained fields, key-based dependency

USA postcodes data source::
    
    http://www.boutell.com/zipcodes/
    http://www.boutell.com/zipcodes/zipcode.zip

Geographic configuration::

    As of now the configuration available includes only USA. If you have to
    validates other countries, you have build similar configuration files and 
    place them in the corresponding folders.

Postcodes validation warning:: 

    If you plan to do USA postcodes validation based on the included YAML 
    file, expect a high memory usage as the file contains ~44000 postcodes.
    A better alternative would be to dump the file in a database, build 
    necessary callables to read the data and instruct formv to use these 
    callables. See formv/configuration.py for an example.
 
Notes::

    Some code fragments have been "borrowed" from FormEncode.

Source:: 

    http://pypi.python.org/pypi/formv

Example:: 

    # schema validation including file upload, file transformation and file recovery 

    import os, formv
    from formv.configuration import build
    from formv.validators import *
    from formv.exception import Invalid
    
    from formv.utils import dict_object
    from formv.utils.compat import PY2
    from formv.utils.fileinfo import BaseFileInfo, ReusedFileInfo 
    
    from tests import multipart
    from examples import to_str, make_environ as env
    
    from datetime import datetime
    from mimetypes import guess_type
    from webob import Request, Response
    
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    formv.config = build(config_root=os.path.join(app_root, 'tests'))
    
    session = dict_object(files=dict_object())
     
    class WebForm(VSchema):     
        fields = {         
            'first_name': VString(min_len=3, max_len=50), 
            'last_name': VString(min_len=3, max_len=50), 
            'postcode': VString(), 
            'state': VString(),
            'country': VCountry(required=True, mode='by-name'), 
            'email': VEmail(required=True), 
            'password': VPassword(special_chars=3),
            'file_upload': VPipe(VUploadFile(), 
                                 VWatermarkImage(type='image', 
                                                 file=os.path.join(app_root, 'tests/watermarks/copyright.jpg'), 
                                                 opacity=.04, angle=45), 
                                 VWatermarkImage(text='formv text watermark', angle=25, 
                                                 color=(0,0,0,128), opacity=1), 
                                 VImprintImage(text='Note the image watermark in the background',  
                                               color=(0,128,128,255)), 
                                 VImprintImage(text=datetime.strftime(datetime.utcnow(),  
                                                                      'Uploaded on %Y/%m/%d - %H:%M:%S GMT'), 
                                               color=(255,128,128,255), 
                                               margin=(25,10)), 
                           ) 
        } 
    
        chains = { 
            'coordinates': VCountryPostcode(country_field='country',     # (latitude, longitude) 
                                     postcode_field='postcode'),         
            'password': VEncodedPair(required_field='password', 
                                     required_label='Password', 
                                     available_field='email'),
            'state': VState(country_field='country', 
                            state_field='state', mode='by-name'),
        } 
         
    class Application(object):
        def __call__(self, environ, start_response):
            self.request = Request(make_environ())  
            response = self.request.get_response(self.response())
            return response(self.request.environ, start_response)
        
        def response(self):
            try:
                form = self.validate(self.request.POST) # - form validation
                body = to_str(form)
            except Invalid as e:
                # - recover successfully uploaded files 
                if isinstance(e.value.get('file_upload'), BaseFileInfo): 
                    session.files['file_upload'] = ReusedFileInfo(e.value['file_upload']) 
                                    
                body = e.message
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
                           replace_empty_value=True, 
                           empty_values={ 
                               # injects recovered file back into form if no new file has been uploaded 
                               'file_upload': session.files.get('file_upload'), 
                           }) 
            return form.validate(request) 
                
    application = Application()  
         
    def make_environ():
        ''' simulates a POST request (multipart/form-data) '''
        
        app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        test_files_dir = os.path.join(app_root, 'tests/files')    
        fields = []
    
        # - plain fields
        fields.append(multipart.field('first_name', 'John'))
        fields.append(multipart.field('last_name', 'Smith'))
        fields.append(multipart.field('email', 'dummy@dummy.com'))
        fields.append(multipart.field('postcode', '99501'))
        fields.append(multipart.field('state', 'Alaska'))
        fields.append(multipart.field('country', 'U.S.A.'))
        fields.append(multipart.field('password', 'dummy-secret-password-1'))
        
        # - file upload
        f = os.path.join(test_files_dir, 'test.jpg')
        fields.append(multipart.file('file_upload', filename=f, 
                                     content_type=guess_type(f, False)[0]))            
        return env(*fields)
    
    
    if __name__ == '__main__':
        from wsgiref.simple_server import make_server   
        httpd = make_server('127.0.0.1', 9000, application)
        sn = httpd.socket.getsockname()
        print("Serving HTTP on", sn[0], "port", sn[1], "...")            
        httpd.serve_forever()
     
Output::

    +----------------------------------------------------------------------------------------------------------+
    | Field name  | Field value                                                                                |
    +==========================================================================================================+
    | coordinates | (61.216799, -149.87828)                                                                    |
    +----------------------------------------------------------------------------------------------------------+
    | country     | 'USA'                                                                                      |
    +----------------------------------------------------------------------------------------------------------+
    | email       | 'dummy@dummy.com'                                                                          |
    +----------------------------------------------------------------------------------------------------------+
    | file_upload | dir_path = '/srv/www/public'                                                               |
    |             | file_date = datetime.datetime(2013, 10, 2, 2, 23, 15, 423000)                              |
    |             | file_ext ='.jpg'                                                                           |
    |             | file_name = '8cc8cb20bbd145a980a29f6d6c1b68bd.jpg'                                         |
    |             | file_object = None                                                                         |
    |             | file_path = '/srv/www/public/8cc8cb20bbd145a980a29f6d6c1b68bd.jpg'                         |
    |             | file_size = 5129                                                                           |
    |             | guid_name ='8cc8cb20bbd145a980a29f6d6c1b68bd'                                              |
    |             | html_field = 'file_upload'                                                                 |
    |             | mime_type = 'image/pjpeg'                                                                  |
    |             | orig_name = 'test.jpg'                                                                     |
    |             | thumb_name = '8cc8cb20bbd145a980a29f6d6c1b68bd_th.jpg'                                     |
    |             | thumb_path = '/srv/www/public/8cc8cb20bbd145a980a29f6d6c1b68bd_th.jpg'                     |
    |             | zip_name = None                                                                            |
    |             | zip_path = None                                                                            |
    |             | zip_size = None                                                                            |
    +----------------------------------------------------------------------------------------------------------+
    | first_name  | 'John'                                                                                     |
    +----------------------------------------------------------------------------------------------------------+
    | last_name   | 'Smith'                                                                                    |
    +----------------------------------------------------------------------------------------------------------+
    | password    | '$x-pbkdf2$20$1000$9.i7QtmSZyKEgKPIMY3DBA==$Qn2VqbZLNfq/ZNe9y/MhLf1xeRk.nJmlXNISnNOmJRo='  |
    +----------------------------------------------------------------------------------------------------------+
    | postcode    | '99501'                                                                                    |
    +----------------------------------------------------------------------------------------------------------+
    | state       | 'AK'                                                                                       |
    +----------------------------------------------------------------------------------------------------------+

For usage and more examples, see examples & tests.
        """,
      classifiers=[
      'Development Status :: 4 - Beta',
      'Environment :: Web Environment',
      'Environment :: Other Environment',
      'Intended Audience :: Developers',
      'License :: OSI Approved :: MIT License',      
      'Operating System :: OS Independent',
      'Programming Language :: Python',
      'Programming Language :: Python :: 2',     
      'Programming Language :: Python :: 3',
      'Topic :: Internet :: WWW/HTTP :: Dynamic Content :: CGI Tools/Libraries',
      'Topic :: Software Development :: Libraries :: Python Modules',      
      'Topic :: Utilities',            
      ],
      keywords='HTML form validation conversion transformation schema',
      author='Adrian Cristea',
      author_email='adrian.cristea@gmail.com ',
      license='MIT',
      packages=find_packages('.', exclude=['example*', 'log*', 'test*',]),
      include_package_data=True,
      install_requires=install_requires(),
      zip_safe=False,
)