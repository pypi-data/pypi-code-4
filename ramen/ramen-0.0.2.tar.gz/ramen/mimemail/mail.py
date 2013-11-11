#coding=utf-8

import smtplib
from datetime import datetime
from hashlib import md5
import sys, re
from .misc import *
from .parts import *

from collections import OrderedDict as odict

class Mimemail():
    
    def __init__(self, **kwargs):
        self.headers = odict()
        self.headers['MIME-Version'] = '1.0'
        self.headers['From'] = MM_DEFAULT_FROM
        self.headers['Date'] = datetime.utcnow().strftime('%a, %d %b %Y %H:%M:%S GMT')
        
        self.body = ''
        self.html = None
        self.text = None
        self.images = []
        self.attachments = []
        self.charset = 'UTF-8'
        self.recipients = {}
        self.from_email = 'root@localhost'
        self.kw = kwargs
    
    def set_from(self, from_email, from_name):
        self.headers['From'] = '%s <%s>' % (encode_header(from_name, self.charset), from_email)
        self.from_email = from_email
        
    def set_html(self, html):
        self.html = html
        
    def set_text(self, text):
        self.text = text
    
    def add_image(self, image):
        self.images.append(image)
        
    def add_attachment(self, att):
        self.attachments.append(att)
        
    def set_subject(self, subject):
        self.subject = subject

    def create_images_part(self, boundary):
        lines = []
        for image in self.images:
            lines.extend([
                MM_DEFAULT_CRLF,
                '--%s%s' % (boundary, MM_DEFAULT_CRLF),
                image.get_part_header(),
                MM_DEFAULT_CRLF,
                MM_DEFAULT_CRLF,
                image.get_part_body()
            ])
            
        return ''.join(lines)
    
    def create_attachments_part(self, boundary):
        lines = []
        for att in self.attachments:
            lines.extend([
                MM_DEFAULT_CRLF,
                '--%s%s' % (boundary, MM_DEFAULT_CRLF),
                att.get_part_header(),
                MM_DEFAULT_CRLF,
                MM_DEFAULT_CRLF,
                att.get_part_body()
            ])
        
        return ''.join(lines)
        
    def build(self):
        has_html = self.html != None
        has_text = self.text != None
        has_img  = len(self.images) > 0
        has_att  = len(self.attachments) > 0
        
        if has_text and not has_html:
            self.html = MimemailPartHtml(re.sub(r'\n', '<br>', self.text.plain_content, re.M | re.S), charset = self.charset)
        elif has_html and not has_text:
            self.text = MimemailPartText(re.sub(r'<|>|/', '', self.html.plain_content, re.M | re.S | re.U), charset = self.charset)
        elif not has_html and not has_text and not has_att:
            raise MimemailException('An email has no content to send')
            
        if has_img:
            for image in self.images:
                src = image.get_file_path()
                dst = 'cid:' + image.get_image_cid()
                self.html.plain_content = self.html.plain_content.replace(os.path.basename(src), dst)
        
        boundary = 'alt_' + gen_boundary_hash()
        self.headers['Content-Type'] = 'multipart/alternative; boundary="' + boundary + '"'
        
        self.body = ''.join([
            '--%s%s' % ( boundary, MM_DEFAULT_CRLF ),
            self.text.get_part_header(),
            MM_DEFAULT_CRLF,
            MM_DEFAULT_CRLF,
            self.text.get_part_body(),
            '%s--%s%s' % ( MM_DEFAULT_CRLF, boundary, MM_DEFAULT_CRLF ),
            self.html.get_part_header(),
            MM_DEFAULT_CRLF,
            MM_DEFAULT_CRLF,
            self.html.get_part_body(),
            '%s--%s--%s%s' % ( MM_DEFAULT_CRLF, boundary, MM_DEFAULT_CRLF, MM_DEFAULT_CRLF )
        ])
        
        if has_img:
            boundary = 'rel_' + gen_boundary_hash()
            self.body = ''.join([
                '--%s%s' % ( boundary, MM_DEFAULT_CRLF ),
                'Content-Type: %s%s%s' % (self.headers['Content-Type'], MM_DEFAULT_CRLF, MM_DEFAULT_CRLF),
                self.body,
                self.create_images_part(boundary),
                '%s--%s--%s%s' % ( MM_DEFAULT_CRLF, boundary, MM_DEFAULT_CRLF, MM_DEFAULT_CRLF )
            ])
            self.headers['Content-Type'] = 'multipart/related; boundary="%s"' % (boundary)
            
        if has_att:
            boundary = 'att_' + gen_boundary_hash()
            self.body = ''.join([
                '--%s%s' % (boundary, MM_DEFAULT_CRLF ),
                'Content-Type: %s%s%s' % (self.headers['Content-Type'], MM_DEFAULT_CRLF, MM_DEFAULT_CRLF),
                self.body,
                self.create_attachments_part(boundary),
                '%s--%s--%s%s' % ( MM_DEFAULT_CRLF, boundary, MM_DEFAULT_CRLF, MM_DEFAULT_CRLF )
            ])
            self.headers['Content-Type'] = 'multipart/mixed; boundary="%s"' % (boundary)
            
        self.headers['Message-ID'] = self.gen_message_id()
        
        if hasattr(self, 'subject'):
            self.headers['Subject'] = encode_header(self.subject, self.charset)
        
    def gen_message_id(self):
        return '<%s.%08x@%s>' % (datetime.datetime.now().strftime('%Y%m%d%H%M%S'), random.randint(0, sys.maxint), self.kw.get('host', 'localhost'))

    def add_recipient(self, email, name = None):
        self.recipients[email] = name if name else email

    def send(self):
        self.build()
        
        extra_headers = self.get_extra_headers()
        
        for email, name in self.recipients.iteritems():
            message = '%s%sTo: %s <%s>%s%s%s' % (extra_headers, MM_DEFAULT_CRLF, encode_header(name, self.charset), email, MM_DEFAULT_CRLF, MM_DEFAULT_CRLF, self.body)
            s = smtplib.SMTP(self.kw.get('smtp_relay', '127.0.0.1'))
            s.sendmail(self.from_email, email, message)
            s.quit()
        
    def get_extra_headers(self):
        return MM_DEFAULT_CRLF.join([ '%s: %s' % (k, v) for k,v in self.headers.iteritems() ])


