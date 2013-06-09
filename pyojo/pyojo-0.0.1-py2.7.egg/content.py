# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2013 nabla.net
# ----------------------------------------------------------------------------
""" Response handlers to be returned by Request.get_response. 

"""
import os
import json

import pyojo.js as js
import pyojo.base as base
import pyojo.data as data
from .func import log, raw_str, pretty, jsbeautify, jsb_opts
from .func import html_escape, html_highlighter



class Custom(base.ContentType):
    """ Send a Reply custom subclass.
    """
    handle = base.Reply
    
    def __call__(self, request):
        print "<--- RESPONSE %s" % self.response
        if "*" in self.response.content:
            log.warning("Content-Type Header set to %s", self.response.content)
        request.content_type(self.response.content)
        return self.response


        
class Status(base.ContentType):
    """ Send status code.
    """
    handle = (type(None), int)
               
    def __call__(self, request):
        status = self.response
        if status is None:
            log.warning("No response for %s", request.url)
            if request.status == 102: #Status is still processing
                status = 404 #Not Found
            elif request.status == 200: #Status is set to OK
                status = 204 #No content
        
        request.status = status
        html = data.TAG("HTML")
        html.head.title += request.response_header["Server"]
        html.body.p.b += "%s %s" % (status, data.HTTP_STATUS[status])
        html.body.pre += "%s" % request.error_info
        request.content_type("text/html")
        return [str(html)]
    
        

class Text(base.ContentType):
    """ Send a string.
    """
    handle = basestring   
    
    def __init__(self, text):
        
        if type(text).__name__ == "unicode":
            self.text = text.encode("utf-8")
        else:
            self.text = text

    def __call__(self, request):
        if request.response_header["Content-Type"] is None:
            request.content_type("text/plain")        
        request.status = 200
        return [self.text]

    def see(self, request):
        request.status = 200
        
        if "text/html" in request.response_header["Content-Type"]:
            return [html_highlighter(html_escape(self.text))]
        if "text/javascript" in request.response_header["Content-Type"]:
            if jsbeautify is not None:
                text = jsbeautify(self.text, jsb_opts)
            else:
                text = self.text
            request.content_type("text/html")
            return [html_highlighter(text)]
        return [self.text]
      

class JavaScript(Text):
    """ Send JavaScript code.
    """
    handle = js.Code

    def __init__(self, response):
        self.response = response
    
    def __set_text(self):
        self.text = self.response.code()
        if type(self.text)!=type(""):
            self.text = self.text.encode('utf8') 
    
    def __call__(self, request):
        request.content_type("text/javascript")
        self.response.catch = True
        self.__set_text()
        return super(JavaScript, self).__call__(request)

    def see(self, request):
        request.content_type("text/javascript")
        self.response.catch = False
        self.__set_text()
        return super(JavaScript, self).see(request)
          

class JSON(base.ContentType):
    """ Send JSON data.
    """
    handle = dict

    def __call__(self, request):
        text = json.dumps(self.response)
        #text = js.js_code(self.response)
        request.content_type("application/json")
        return [text]

    def see(self, request):
        text = json.dumps(self.response)
        request.content_type("text/html")
        return [html_highlighter(jsbeautify(text))] 


class FileLike(base.ContentType):
    """ Send a file-like object.
    """
    handle = data.XML
    
    def __call__(self, request):
        
        request.content_type("application/xml")
        #log.debug(response.to_string())
        return self.response.get_file()
        
        
            
class CachedText(base.ContentType):
    """ Stores a text file in memory.
    """
    instances={}
    
    def __new__(cls, url, filename=None):
        try:
            return cls.instances[url]
        except KeyError:
            new = super(CachedText, cls).__new__(cls, url)
            if filename is None:
                return new
            new.load(filename)
            cls.instances[url] = new
            #log.debug("Loaded %s %sb/%sKb", filename, new.size, new.total_size()/1024)
            return new

    def rtype(self):
        return "%s %0.2fKb" % (self.ext, self.size/1024.0) 

    def __init__(self, url, filename=None):
        """ The constructor has done all.
        """
        self.url = url

    def total_size(self):
        b = 0
        for url in self.instances.keys():
            b +=self.instances[url].size
        return b

    def load(self, filename):
        with open(filename, 'r') as f:
            self.text = f.read()   
        self.ext = os.path.splitext(filename)[1][1:]        
        self.size = os.path.getsize(filename)
        self.loaded = True

    def __call__(self, request):
        request.response_header["Content-Type"] = data.MIMETYPE[self.ext]    
        request.response_header["Content-Length"] = self.size
        request.handler_info = "%s %s" % ("Cached", self.url)
        request.status = 200
        return [self.text]
            

            
            
class FileSystem(base.ContentType):
    """A file to be sent.
    """
        
    def __init__(self, path):
        self.path = path
        self.ext = os.path.splitext(path)[1][1:]
        self.size = os.path.getsize(path)

    def rtype(self):
        return "%s %0.2fKb" % (self.ext, self.size/1024.0) 

    def __call__(self, request):
        filelike = file(self.path, 'rb')
        request.status=200
        request.response_header["Content-Type"] = data.MIMETYPE[self.ext]    
        request.response_header["Content-Length"] = self.size       
        block_size = 4096
        if 'wsgi.file_wrapper' in request.environ:
            return request.environ['wsgi.file_wrapper'](filelike)#, block_size)
        else:
            return iter(lambda: filelike.read(block_size), '')
        
        



 

class ErrorMsg(base.ContentType):
    """An error message.
    """
    handle = base.Traceback

    def __call__(self, request):
        tb = self.response
        text = tb.trace + "%s" % tb + "\n\n"+pretty(tb.info)
        #if not request.async: 
        #    request.content_type("text/plain")
        #    return [text]
        request.content_type("text/javascript")
        request.status = 200
        code = js.Alert("Error at %s" % raw_str(str(tb)),
                        "<pre>%s</pre>" % raw_str(text)).code() 
        print code #FIX
        return [code]

    def see(self, request):
        tb = self.response
        text = tb.trace + "%s" % tb + "\n\n"+pretty(tb.info)
        request.content_type("text/html")
        request.status = 200
        return ["<p>Error <b>%s</b><p>" % tb,
                "<pre>%s</pre>" % text]
        
class Page(base.ContentType):
    """ A HTML page.
    """
    content="text/html"


class Image(base.ContentType):
    """ A generated image file.
    """
    content="image/*"


class Stream(base.ContentType):
    """A octec stream.
    """
    content="application/octet-stream"


class Download(base.ContentType):
    """A file to be sent as an attachment.
    """
    content="*/*"
    #self.set_header("Content-Disposition", "attachment; filename="+filename)






 
        
#----------------------------------------------------------------------------
