#coding=utf-8

from .misc import *
import os
from collections import OrderedDict as odict

class MimemailPart(object):
    image_types = {
        'gif':  'image/gif',
        'jpg':  'image/jpeg',
        'jpeg': 'image/jpeg',
        'jpe':  'image/jpeg',
        'png':  'image/png',
        'tif':  'image/tiff',
        'tiff': 'image/tiff',
        'swf':  'application/x-shockwave-flash'
    }
    
    def __init__(self):
        self.part_type = ''
        self.boundary = ''
        self.body = ''
        self.headers = odict
        self.plain_content = ''
        self.charset = 'UTF-8'
        
    def get_part_header(self):
        if len(self.headers):
            return MM_DEFAULT_CRLF.join([ '%s: %s' % (k,v) for k,v in self.headers.iteritems() ])
        return ''
        
    def get_part_body(self):
        return self.body
    
    def get_part_type(self):
        return self.part_type
    
    
class MimemailPartImage(MimemailPart):
    def __init__(self, filepath, content_type = None, content = None):
        super(MimemailPartImage, self).__init__()
        self.part_type = 'IMAGE'
        self.cid = gen_boundary_hash()
        self.image_file = filepath
        name = os.path.basename(filepath)
        if content_type:
            self.headers['Content-Type'] = content_type
        else:
            ext = name[name.rfind('.')+1:].lower()
            if ext in self.image_types:
                self.headers['Content-Type'] = '%s; name="%s"' % (self.image_types[ext], name)
            else:
                self.headers['Content-Type'] = 'application/octet-stream; name="%s"' % name
                
        self.headers['Content-Transfer-Encoding'] = 'base64'
        self.headers['Content-Disposition'] = 'inline; filename="%s"' % name
        self.headers['Content-ID'] = '<%s>' % self.cid
        
        if not content:
            f = open(filepath, 'rb')
            self.body = f.read()
            f.close()
        else:
            self.body = content
        
        self.body = encode_content(self.body)
        
    def get_image_cid(self):
        return self.cid
    
    def get_file_path(self):
        return self.image_file
    
    
class MimemailPartAttachment(MimemailPart):
    def __init__(self, filepath, content_type = 'application/octet-stream', content = None):
        super(MimemailPartAttachment, self).__init__()
        self.part_type = 'ATTACHMENT'
        
        if not content:
            f = open(filepath, 'rb')
            self.body = f.read()
            f.close()
        else:
            self.body = content
        
        self.body = encode_content(self.body)
        
        self.headers['Content-Type'] = '%s; name="%s"' % (content_type, os.path.basename(filepath))
        self.headers['Content-Transfer-Encoding'] = 'base64'
        self.headers['Content-Disposition'] = 'attachment; filename="%s"' % os.path.basename(filepath)
        
    
class MimemailPartText(MimemailPart):
    def __init__(self, text, **kwargs):
        super(MimemailPartText, self).__init__()
        self.part_type = 'TEXT'
        self.headers['Content-Type'] = 'text/plain; charset="%s"' % kwargs.get('charset', 'UTF-8')
        self.headers['Content-Transfer-Encoding'] = 'base64'
        self.plain_content = text
        self.body = encode_content(text)
    
    
class MimemailPartHtml(MimemailPart):
    def __init__(self, html, **kwargs):
        super(MimemailPartHtml, self).__init__()
        self.part_type = 'HTML'
        self.headers['Content-Type'] = 'text/html; charset="%s"' % kwargs.get('charset', 'UTF-8')
        self.headers['Content-Transfer-Encoding'] = 'base64'
        self.plain_content = html

    def get_part_body(self):
        return encode_content(self.plain_content)
