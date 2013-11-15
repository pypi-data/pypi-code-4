#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import unittest, os, zipfile, logging
from cgi import FieldStorage
from io import BytesIO
from mimetypes import guess_type
from datetime import datetime
from formv.exception import Invalid
from formv.validators.compound import VPipe
from formv.validators.strings import VEmail
from formv.validators.files import *
from formv.utils.encoding import encode
from tests import multipart 
from formv.utils.compat import PY2, PY3
if PY2:
    import ImageFont
if PY3:
    try:
        import ImageFont
    except ImportError:        
        from PIL import ImageFont

log = logging.getLogger(__name__)

class Test(unittest.TestCase):
    def test_upload(self):
        app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        test_files_dir = os.path.join(app_root, 'tests/files')    
        test_files = []
        
        for root, _, files in os.walk(test_files_dir):
            for f in files:
                test_files.append(os.path.join(root, f))

        body = []; boundary = 'dummy';
        start_boundary = encode('--%s' % boundary) 
        end_boundary = encode('--%s--' % boundary)
        
        for i, tf in enumerate(test_files):
            body.append(multipart.file('dummy_file_' + str(i), filename=tf, 
                                        content_type=guess_type(tf)[0]))            
        
        body = start_boundary.join(body)
        body = b''.join([start_boundary, body, end_boundary])
        
        environ = {
            'REQUEST_METHOD':'POST',
            'CONTENT_TYPE':'multipart/form-data; boundary=%s' % boundary,
            'CONTENT_LENGTH':len(body)
        }
        
        fs = FieldStorage(fp=BytesIO(body), environ=environ, 
                          keep_blank_values=1, strict_parsing=1)
        
        for f in fs.list:
            orig_name = os.path.split(f.filename)[1]
            if orig_name == 'test.tif':
                self.assertRaises(Invalid, VUploadFile().validate, *(f,))
            else:
                fi = VPipe(VUploadFile(), 
                           VWatermarkImage(type='image',
                                           file=os.path.join(app_root, 'tests/watermarks/copyright.jpg'),
                                           opacity=.04, angle=45),
                           VWatermarkImage(text='formv text watermark', angle=25,
                                           color=(0,0,0,128), opacity=1),
                           VImprintImage(text='Note the image watermark in the background', 
                                         color=(0,128,128,255),),                           
                           VImprintImage(text=datetime.strftime(datetime.utcnow(), 
                                                                'Uploaded on %Y/%m/%d - %H:%M:%S GMT'),
                                         color=(255,128,128,255),
                                         margin=(25,10),),
                           ).validate(f)                
                           
                self.assertEqual(orig_name, fi.orig_name)
                if fi.mime_type in ('image/png', 'image/x-png', 'image/gif', 
                                    'image/jpeg', 'image/pjpeg'):                    
                    self.assertTrue(os.path.isfile(fi.file_path))                    
                else:
                    self.assertTrue(os.path.isfile(fi.zip_path))
                    zf = zipfile.ZipFile(fi.zip_path, 'r', zipfile.ZIP_DEFLATED)
                    self.assertEqual(fi.file_size, zf.getinfo(fi.orig_name).file_size)

    def test_text_to_image(self):
        app_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        font_files_dir = os.path.join(app_root, 'tests/fonts')    
        font_files = []
        
        for root, _, files in os.walk(font_files_dir):
            for f in files:
                font_files.append(os.path.join(root, f))
        
        text, file_info = VTextToImage(dir_path='/srv/www/text').validate('dummy')        
        self.assertEqual('dummy', text)
        self.assertTrue(os.path.isfile(file_info.file_path))
         
        email, file_info = VPipe(VEmail(), VTextToImage(dir_path='/srv/www/email')).validate('dummy@dummy.com')        
        self.assertEqual('dummy@dummy.com', email)
        self.assertTrue(os.path.isfile(file_info.file_path))
         
        for f in font_files:
            try:
                font = ImageFont.truetype(f, 12)
                email, file_info = VPipe(VEmail(), 
                                         VTextToImage(dir_path='/srv/www/email', 
                                                      font=font)).validate('dummy@dummy.com')        
                self.assertEqual('dummy@dummy.com', email)
                self.assertTrue(os.path.isfile(file_info.file_path))
            except ImportError as e: # - the _imagingft C module is not installed
                log.error(e)

