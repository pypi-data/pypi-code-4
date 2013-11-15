#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

""" How to reuse uploaded files, if file validation has 
    succeeded, but overall form validation has failed. 
    
    Also how to install a new language to be used with formv
"""

import os, logging, formv
from mimetypes import guess_type
from webob import Request, Response

from formv.configuration import build
from formv.validators import *
from formv.exception import Invalid

from formv.utils.compat import PY2
from formv.utils import dict_object
from formv.utils.fileinfo import BaseFileInfo, ReusedFileInfo
from tests import multipart
from examples import to_str, make_environ as env

logging.basicConfig(filename='../logs/formv.log', level=logging.DEBUG,
                    format='[%(asctime)s][%(levelname)s][%(filename)s] %(message)s %(name)s %(funcName)s (line: %(lineno)d)')
log = logging.getLogger(__name__)

app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
formv.config = build(config_root=os.path.join(app_root, 'tests'))

reload_count = 0
session = dict_object(files=dict_object())

from formv.utils import install_language
install_language(languages=['test',])

class Application(object):    
    def __call__(self, environ, start_response):
        self.request = Request(make_environ()) # - use prepared environ 
        response = self.request.get_response(self.response())
        return response(self.request.environ, start_response)
    
    def response(self):
        body = '<h3>Refresh this page at least once</h3>'
        try:
            form = self.validate(self.request.POST)

            body += '<b>form validation successful</b>'
            body += to_str(form)
            session.files.clear()
            
        except Invalid as e:
            # - recover successfully uploaded files
            for f in ('file_pdf','file_jpg','file_dummy'):                
                if isinstance(e.value.get(f), BaseFileInfo):
                    session.files[f] = ReusedFileInfo(e.value[f])

            for f in ('file_pdf','file_jpg','file_dummy'):                
                if isinstance(e.value.get(f), ReusedFileInfo):            
                    body += 'file %s was reused<br/>' % e.value[f].orig_name

            body += '<br/>' + e.message + '<br/>'
            body += '<br/>errors'
            body += to_str(e.errors)
            body += '<br/>values'
            body += to_str(e.value)

        global reload_count
        reload_count += 1
        
        response = Response()    
        response.text = unicode(body) if PY2 else body
        return response
        
    def validate(self, request):
        form = WebForm(allow_missing_keys=True,
                       allow_extra_keys=True,
                       replace_missing_key=True,
                       missing_key_value='dummy',
                       replace_empty_value=True,
                       empty_values={ 
                           # inject recovered files back into form 
                           # if no new files have been uploaded
                           'file_pdf': session.files.get('file_pdf'),
                           'file_jpg': session.files.get('file_jpg'),
                           'file_dummy': session.files.get('file_dummy'),
                       })    
        return form.validate(request)
            
application = Application()   


class WebForm(VSchema):
    fields = {
        'email': VEmail(required=True),
        'file_pdf': VPipe(VUploadFile(required=True), 
                          VWatermarkImage(text='watermark'),
                          VImprintImage(text='imprint')),
        'file_jpg': VPipe(VUploadFile(), 
                          VWatermarkImage(text='watermark'),
                          VImprintImage(text='imprint')),
        'file_dummy': VPipe(VUploadFile(required=True), 
                            VWatermarkImage(text='watermark'),
                            VImprintImage(text='imprint')),
    }


def make_environ():
    """ simulates a POST request (multipart/form-data) """
    
    app_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    test_files_dir = os.path.join(app_root, 'tests/files')    
    fields = []
    
    # - plain fields
    fields.append(multipart.field('email', 'invalid email'))
    
    # - files upload
    if reload_count == 0: # simulates a one-time files upload
        f = os.path.join(test_files_dir, 'test.pdf')
        fields.append(multipart.file('file_pdf', filename=f, 
                                     content_type=guess_type(f, False)[0]))            
        
        f = os.path.join(test_files_dir, 'test.jpg')
        fields.append(multipart.file('file_jpg', filename=f, 
                                     content_type=guess_type(f, False)[0]))            
        fields.append(multipart.empty('file_dummy'))
    else:
        fields.append(multipart.empty('file_pdf'))        
        fields.append(multipart.empty('file_jpg'))
        fields.append(multipart.empty('file_dummy'))        
    
    return env(*fields)


if __name__ == '__main__':
    from wsgiref.simple_server import make_server   
    httpd = make_server('127.0.0.1', 9000, application)
    sn = httpd.socket.getsockname()
    print("Serving HTTP on", sn[0], "port", sn[1], "...")            
    httpd.serve_forever()

        
        
        
