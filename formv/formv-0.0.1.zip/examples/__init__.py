#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

from io import BytesIO
from formv.utils.encoding import encode
from formv.exception import Invalid

def make_environ(*fields):
    """ builds a multipart/form-data, wsgi-compatible environment """
    body = []; boundary = 'dummy';
    start_boundary = encode('--%s' % boundary) 
    end_boundary = encode('--%s--' % boundary)
    
    body.extend(fields)
    body = start_boundary.join(body)
    body = b''.join([start_boundary, body, end_boundary])
    
    environ = {
        'SERVER_NAME':'localhost',
        'SERVER_PORT':9000,
        'SERVER_PROTOCOL':'HTTP/1.1',
        'REQUEST_METHOD':'POST',
        'CONTENT_TYPE':'multipart/form-data; boundary=%s' % boundary,
        'CONTENT_LENGTH':len(body),
        'QUERY_STRING':'',
        'wsgi.input':BytesIO(body),
        'wsgi.url_scheme':'http'
    }    
    return environ


def _to_str(k, v, level=0):
    out=''
    if hasattr(v, 'items'):
        out += '<tr><td valign=top>' + str(k) + '</td><td>'
        out += '<table border=1 cellpadding=3 cellspacing=0>'
        for k_ in sorted(v.keys()):
            level += 1               
            out += _to_str(k_, v.get(k_), level)
            level -= 1
        out += '</table>'
        out += '</td></tr>'
    elif isinstance(v, Invalid):
        out += '<tr><td valign=top>' + str(k) + '</td><td>'
        out += '<table border=1 cellpadding=3 cellspacing=0>'
        for k_ in sorted(v.value.keys()):
            level += 1               
            out += _to_str(k_, v.value.get(k_), level)
            level -= 1
        out += '</table>'
        out += '</td></tr>'

        out += '<tr><td valign=top>' + str(k) + '</td><td>'
        out += '<table border=1 cellpadding=3 cellspacing=0>'
        for k_ in sorted(v.errors.keys()):
            level += 1               
            out += _to_str(k_, v.errors.get(k_), level)
            level -= 1
        out += '</table>'
        out += '</td></tr>'        
    else:
        out += '<tr><td valign=top>' + str(k) + '</td><td valign=top>' + repr(v) + '</td></tr>'
    return out   

def to_str(d):
    return '<table border=0 cellpadding=3 cellspacing=0>' + _to_str('', d) + '</table>'