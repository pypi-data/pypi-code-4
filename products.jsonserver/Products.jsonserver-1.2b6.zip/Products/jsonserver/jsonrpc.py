##############################################################################
#
# Copyright (c) 2005 Zope Corporation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################

__docformat__ = 'restructuredtext'


try:
    import simplejson as json
except ImportError:
    import json
from zExceptions.ExceptionFormatter import format_exception
from zExceptions import Unauthorized
import sys, re
from zLOG import LOG, INFO, DEBUG, ERROR
from cgi import FieldStorage
import  ZPublisher.HTTPResponse
from zope.interface import alsoProvides
from Products.jsonserver.interfaces import IJsonRequest
from types import TupleType

# this is used to identify incoming requests
request_content_types = frozenset(['application/json-rpc', 'application/json'])
request_content_type = 'application/json'
# this will be set on the response
response_content_type = 'application/json'

# marker of marshalled keywords
pythonkwmarker = 'pythonKwMaRkEr'

VERSION = "1.1"

def get_response(obj, input_encoding):
    content_type = response_content_type + ';charset=utf-8'
    cooked_obj = json.dumps(obj, encoding=input_encoding)
    return content_type, cooked_obj

def parse_input(data, encoding):
    """Parse input data and return a method path and argument tuple

    The data is a string.
    """
    # make the data to unicode
    if not isinstance(data, unicode):
        try:
            data = data.decode(encoding)
        except UnicodeDecodeError:
            try:  
                data = data.decode('utf-8')
            except UnicodeDecodeError:
                data = data.decode('ascii', 'ignore')
    data = json.loads(data)
    functionstr = data[u'method'].encode('utf-8')
    if functionstr:
        method = functionstr.replace('.', '/')
    else:
        method = None
    jsonID = data[u'id']
    params = data[u'params'] or []
    # Translate '.' to '/' in meth to represent object traversal.
    method = method.replace('.', '/')
    LOG('jsonserver', DEBUG, "processing request %s" % (data, ))

    # Separare positional keywords from args
    # this works if client emits {'jsonclass': ['zope.kw', kw]}
    args, kw = [], {}
    for arg in params:
        success = False
        if isinstance(arg, dict) and 'jsonclass' in arg:
            # json class hints
            # TODO handle Date
            pass
        elif isinstance(arg, dict) and pythonkwmarker in arg:
            # a keyword parm
            kw.update(arg[pythonkwmarker])
            success = True
        if not success:
            # a normal positional parm
            args.append(arg)

    return jsonID, method, args, kw

class Response:
    '''Customized Response
    '''
    # use delegation, rather than inheritance

    def __init__(self, real, jsonID):
        self.__dict__['_real'] = real
        self.__dict__['_jsonID'] = jsonID
        real._encode_unicode = self._encode_unicode

    def __getattr__(self, name): return getattr(self._real, name)
    def __setattr__(self, name, v): return setattr(self._real, name, v)
    def __delattr__(self, name): return delattr(self._real, name)

    def _response_encoding(self, charset_re=re.compile(r'(?:application|text)/[-+0-9a-z]+\s*;\s*' +
                                              r'charset=([-_0-9a-z]+' +
                                              r')(?:(?:\s*;)|\Z)',
                                              re.IGNORECASE)):
        'based on ZPublisher.HTTPResponse._encode_unicode'
        # if the encoding is specified, return that
        if 'content-type' in self.headers:
            match = charset_re.match(self.headers['content-type'])
            if match:
                encoding = match.group(1)
                return encoding
        # Use the default character encoding
        # (by default 'iso-8859-15', but
        # it may get overwritten during configuration)
        try:
            return ZPublisher.HTTPResponse.default_encoding
        except AttributeError:
            # older versions of Zope (e.g. 2.8.1-final) do not have default_encoding,
            # they default to 'iso-8859-15'
            return 'iso-8859-15'

    def setBody(self, body, title='', is_error=0, bogus_str_search=None):
        """return
        {
        'id' : matches id in request
        'result' : the result or null if error
        'error' : the error or null if result
        }
        """
        if self._jsonID is None:
            self._real.setBody('')
            self._real.setStatus(204)
            LOG('jsonserver', DEBUG, "processing response 204 for id=%s" % (self._jsonID, ))
        else:
            body = premarshal(body)
            wrapper = {'id':self._jsonID}
            wrapper['result'] = body
            LOG('jsonserver', DEBUG, "processing response %s" % (wrapper, ))
            response_encoding = self._response_encoding()
            content_type, cookedbody = get_response(wrapper, response_encoding)
            self._real.setHeader('content-type', content_type)
            self._real.setBody(cookedbody)
            self._real.setStatus(200)
        return self

    def exception(self, fatal=0, info=None,
                  absuri_match=None, tag_search=None):
        # Fetch our exception info. t is type, v is value and tb is the
        # traceback object.
        if type(info) is TupleType and len(info)==3:
            t, v, tb = info
        else:
            t, v, tb = sys.exc_info()

        if t in ('Unauthorized', Unauthorized):
            status = 401
        else:
            status = 200
            LOG('jsonserver', ERROR, 'Exception caught:' + '\n'.join(format_exception(t, v, tb)))

        error = {'name': 'JSONRPCError',
                 'code': 500,
                 'message':'%s: %s' % (getattr(t, '__name__', t), v)}
        wrapper = {'id': self._jsonID, 'version': VERSION, 'error': error}

        self._real.setHeader('content-type', response_content_type)
        self._real.setBody(json.dumps(wrapper))
        self._real.setStatus(status)

        #TODO What should really happen on error in a notification?

response=Response

def premarshal_dict(data):
    """return a non-proxied dict"""
    return dict([(premarshal(k), premarshal(v))
                 for (k, v) in data.items()])

def premarshal_list(data):
    """return a non-proxied list"""
    return map(premarshal, data)

#note: no dates or datetimes in json, but supported by xmlrpc
premarshal_dispatch_table = {
    dict: premarshal_dict,
    list: premarshal_list,
    tuple: premarshal_list,
    }

premarshal_dispatch = premarshal_dispatch_table.get

def premarshal(data):
    premarshaller = premarshal_dispatch(data.__class__)
    if premarshaller is not None:
        return premarshaller(data)
    return data

# --
# Patching processInputs of ZPublisher.HTTPRequest
# --

re_content_type= re.compile(r'charset\s*=\s*([^;]+)')

def processInputs(self, **kw):
    'Process request inputs'
    response=self.response
    environ=self.environ
    method=environ.get('REQUEST_METHOD','GET')

    if method != 'GET': fp=self.stdin
    else:               fp=None

    form=self.form
    other=self.other

    meth=None
    fs=FieldStorage(fp=fp,environ=environ,keep_blank_values=1)

    # Fix broken content types of Opera
    # this is because the xmlHTTPRequest method cannot set
    # the headers so it will always send text/xml;... ,
    # but we want to identify the requests regardless!
    ct = fs.headers.get('content-type', '')
    if ct.startswith('text/xml') and \
            isinstance(fs.value, str) and fs.value.startswith('{"id":'):
        fs.headers['content-type'] = request_content_type
    if ct.split(';', 1)[0] in request_content_types and method == 'POST':
        # get the content charset, suppose utf-8 if not given.
        match = re_content_type.search(ct, re.I)
        if match is not None:
            charset = match.group(1)
        else:
            charset = 'utf-8'
        jsonID, meth, self.args, keywords = parse_input(fs.value, charset)
        # set the keywords on the form
        for key, value in keywords.iteritems():
            # make sure key is not unicode, but normal string!
            # XXX TODO Cannot decide the right policy here.
            ##key = key.encode(charset)
            key = key.encode('iso-8859-15', 'replace')
            form[key] = value
        # set the marker that can be used to check if we are in json mode
        other['JSON_MODE'] = self.json_mode = True
        # also set the request interface
        alsoProvides(self, IJsonRequest)
        #
        response = Response(response, jsonID)
        other['RESPONSE'] = self.response = response
        self.maybe_webdav_client = 0
        # continue with what used to be at the end of processInputs
        if 'PATH_INFO' in environ:
            path=environ['PATH_INFO']
            while path[-1:]=='/': path=path[:-1]
        else: path=''
        other['PATH_INFO']=path="%s/%s" % (path,meth)
        self._hacked_path=1
        return self
    else:
        if self.stdin is not None:
            self.stdin.seek(0)
        return self._processInputs_jsonrc_patched(**kw)

from ZPublisher.HTTPRequest import HTTPRequest
def patch_HTTPRequest():
    'This will patch HTTPRequest to enable json-rpc handling'
    HTTPRequest._processInputs_jsonrc_patched, HTTPRequest.processInputs = \
        HTTPRequest.processInputs, processInputs
    LOG('jsonserver', INFO, '*** Patching ZPublisher.HTTPRequest for json-rpc ***')
