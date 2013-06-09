# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" Classes for data manipulation.
"""
import StringIO
import xml.etree.ElementTree as etree
from .func import DataError

class Array(dict):
    """ A dojo.JsonRest friendly store
    """
    __slots__ = ()
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__
    __getitem__ = dict.get
    __getattr__ = dict.get
    __getstate__ = lambda self: None
    __copy__ = lambda self: Array(self)




class Structure(object):
    """ A tree of elements with unique id.
    """
    def __init__(self):
        self.items={}

    def add(self, key):
        self.items[key]=set()
        
    def __setitem__(self, key, value):
        if not self.items.has_key(key):
            self.items[key]=set()
        self.items[key].add(value)

    def __getitem__(self, key):
        if self.items.has_key(key):
            return self.items[key]
        for value in self.items.values():
            if key in value: return set()
        return None
    
    def __repr__(self):
        return repr(self.items)


class DefaultDict(dict):
    """ A dictionary with a default value.
    """
    def __init__(self, *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.default = None

    def __getitem__(self, key):
        return dict.get(self, self.default)

class LimitedDict(dict):
    """ A dictionary with allowed keys.
    
        To avoid setting wrong headers, for example.
    """
    def __init__(self, allowed_key_list=[], *args, **kwargs):
        dict.__init__(self, *args, **kwargs)
        self.keys = allowed_key_list
        self.default = None

    def __setitem__(self, key, value):
        if not key in self.keys:
            raise DataError(key, "Key not allowed.")
            return
        return dict.__setitem__(self, key, value)
        
    def __getitem__(self, key):
        return dict.get(self, key, self.default)



class File(StringIO.StringIO):
    """ Temporal file in memory.
    """
    pass


        

class XML(object):
    """ A eXtensible Markup Language document.
    """
    DTD = None
    stylesheet = None
    
    def __init__(self, tag):
        ''' Create a new XML tree. 
        '''
        self.root = etree.Element(tag)
        self.xml = etree.ElementTree(self.root)
        

    def new_node(self, tag, prop={}, text="", parent=None):
        if not type(prop)==type({}):
            raise DataError(self,
            "Node properties must be a dictionary, not %s" % type(prop).__name__)
        if parent is None:
            parent = self.root
        node = etree.SubElement(parent, tag)
        for p,v in prop.iteritems():
            node.set(p, v)
        node.text = text
        return node


    def get_file(self):
        """ Get a XML file-like object.
        """
        new = File()
        self.to_file(new)
        new.seek(0)
        return new

    def to_file(self, file, xml=True):
        """ Write the XML text to a file-like object.
        """
        encoding = "utf-8"
        #style = '/static/css/xml.css'
        #file.write("<?xml version='1.0' encoding='%s'?>\n" % encoding)
        #file.write("<?xml-stylesheet href='%s' type='text/css'?>" % style)
        self.xml.write(file, encoding = encoding,
                       #xml_declaration=xml,
                       #default_namespace="www.pyojo.com",
                       #method="xml"
                       )

    def to_string(self, xml=True):
        ''' Returns the XML as a string.
        '''
        class dummy: pass
        data = []
        file = dummy()
        file.write = data.append
        self.to_file(file, xml)
        return "".join(data)


class TAG(object): # etree.Element
    def __init__(self, tag, parent=None):
        if parent is None:
            new = etree.Element(tag)
        else:
            new = etree.SubElement(parent, tag)
        self.__dict__["_element"] = new
            
    def __str__(self):
        return etree.tostring(self._element)

    def __call__(self, props={}):
        for k,v in props.iteritems():
            self._element.set(k, v)
        return self

    def __add__(self, element):
        if type(element)==type(self):
            self.__dict__["_element"].append(element._element)
        else:
            if self._element.text is None: 
                self._element.text=""
            self._element.text += "%s" % element
        return self
            
    def __getattr__(self, attr):
        """ Return the attribute, or the node with that name if found.
        
            Only called if __getattribute__ failed
        """
        
        if attr in self.__dict__: #Already created
            return self.__dict__[attr]
        new = TAG(attr, self._element)
        self.__dict__[attr] = new
        return new


    def __setattr__(self, attr, value):
        """ Declaring a child node.
        """
        if attr in self.__dict__:
            self.__dict__[attr]=value
            return
        
            
        

NO_RESPONSE = []

MIMETYPE = {
    '3gp': 'video/3gpp',
    '3gp2': 'video/3gpp2',
    '3gpp': 'video/3gpp',
    '3gpp2': 'video/3gpp2',
    '7z': 'application/x-7z-compressed',
    'arj': 'application/x-arj',
    'asc': 'text/plain',
    'asf': 'video/x-ms-asf',
    'asp': 'application/x-asp',
    'au': 'audio/basic',
    'avf': 'video/x-msvideo',
    'avi': 'video/x-msvideo',
    'bak': 'application/x-trash',
    'bin': 'application/octet-stream',
    'bmp': 'image/bmp',
    'bz': 'application/x-bzip',
    'bz2': 'application/x-bzip',
    'c': 'text/x-csrc',
    'c++': 'text/x-c++src',
    'cab': 'application/vnd.ms-cab-compressed',
    'cap': 'application/vnd.tcpdump.pcap',
    'cgm': 'image/cgm',
    'chm': 'application/vnd.ms-htmlhelp',
    'class': 'application/x-java',
    'css': 'text/css',
    'csv': 'text/csv',
    'cur': 'image/x-win-bitmap',
    'diff': 'text/x-patch',
    'divx': 'video/x-msvideo',
    'doc': 'application/msword',
    'docbook': 'application/x-docbook+xml',
    'dot': 'text/vnd.graphviz',
    'dtd': 'application/xml-dtd',
    'dv': 'video/dv',
    'dwg': 'image/vnd.dwg',
    'dxf': 'image/vnd.dxf',
    'emf': 'image/x-emf',
    'eml': 'message/rfc822',
    'epub': 'application/epub+zip',
    'exe': 'application/x-ms-dos-executable',
    'flac': 'audio/flac',
    'flc': 'video/x-flic',
    'fli': 'video/x-flic',
    'flv': 'video/x-flv',
    'gif': 'image/gif',
    'gtar': 'application/x-tar',
    'gv': 'text/vnd.graphviz',
    'gz': 'application/gzip',
    'htm': 'text/html',
    'html': 'text/html',
    'ico': 'image/vnd.microsoft.icon',
    'jpe': 'image/jpeg',
    'jpeg': 'image/jpeg',
    'jpg': 'image/jpeg',
    'js': 'application/javascript',
    'json': 'application/json',
    'latex': 'text/x-tex',
    'lha': 'application/x-lha',
    'load' : 'text/html', # special
    'log': 'text/x-log',
    'mak': 'text/x-makefile',
    'man': 'application/x-troff-man',
    'manifest': 'text/cache-manifest',
    'markdown': 'text/x-markdown',
    'mbox': 'application/mbox',
    'md': 'text/x-markdown',
    'mdb': 'application/vnd.ms-access',
    'mht': 'application/x-mimearchive',
    'mhtml': 'application/x-mimearchive',
    'mid': 'audio/midi',
    'midi': 'audio/midi',
    'mov': 'video/quicktime',
    'mp2': 'video/mpeg',
    'mp3': 'audio/mpeg',
    'mp4': 'video/mp4',
    'mpe': 'video/mpeg',
    'mpeg': 'video/mpeg',
    'mpg': 'video/mpeg',
    'mpga': 'audio/mpeg',
    'ogg': 'video/x-theora+ogg',
    'ogm': 'video/x-ogm+ogg',
    'ogv': 'video/x-theora+ogg',
    'ogx': 'application/ogg',
    'old': 'application/x-trash',
    'pdf': 'application/pdf',
    'perl': 'application/x-perl',
    'pfa': 'application/x-font-type1',
    'pfb': 'application/x-font-type1',
    'pfx': 'application/x-pkcs12',
    'pgm': 'image/x-portable-graymap',
    'pgn': 'application/x-chess-pgn',
    'pgp': 'application/pgp-encrypted',
    'php': 'application/x-php',
    'png': 'image/png',
    'pnm': 'image/x-portable-anymap',
    'po': 'text/x-gettext-translation',
    'por': 'application/x-spss-por',
    'ppm': 'image/x-portable-pixmap',
    'pps': 'application/vnd.ms-powerpoint',
    'py': 'text/x-python',
    'pyc': 'application/x-python-bytecode',
    'pickle': 'application/python-pickle',
    'pyo': 'application/x-python-bytecode',
    'rar': 'application/x-rar',
    'rdf': 'application/rdf+xml',
    'rdfs': 'application/rdf+xml',
    'reg': 'text/x-ms-regedit',
    'tar': 'application/x-tar',
    'tar.bz': 'application/x-bzip-compressed-tar',
    'tar.bz2': 'application/x-bzip-compressed-tar',
    'tar.gz': 'application/x-compressed-tar',
    'tar.lrz': 'application/x-lrzip-compressed-tar',
    'tar.lzma': 'application/x-lzma-compressed-tar',
    'tar.lzo': 'application/x-tzo',
    'tar.xz': 'application/x-xz-compressed-tar',
    'tar.z': 'application/x-tarz',
    'taz': 'application/x-tarz',
    'tb2': 'application/x-bzip-compressed-tar',
    'tbz': 'application/x-bzip-compressed-tar',
    'tbz2': 'application/x-bzip-compressed-tar',
    'tcl': 'text/x-tcl',
    'tex': 'text/x-tex',
    'texi': 'text/x-texinfo',
    'texinfo': 'text/x-texinfo',
    'tga': 'image/x-tga',
    'tgz': 'application/x-compressed-tar',
    'theme': 'application/x-theme',
    'tif': 'image/tiff',
    'tiff': 'image/tiff',
    'tk': 'text/x-tcl',
    'torrent': 'application/x-bittorrent',
    'txt': 'text/plain',
    'vcard': 'text/vcard',
    'vcf': 'text/vcard',
    'vcs': 'text/calendar',
    'wbmp': 'image/vnd.wap.wbmp',
    'wp': 'application/vnd.wordperfect',
    'wsgi': 'text/x-python',
    'xbm': 'image/x-xbitmap',
    'xcf': 'image/x-xcf',
    'xsl': 'application/xslt+xml',
    'zip': 'application/zip'}


HEADERS_REQUEST = [
    "Accept",
    "Accept-Charset",
    "Accept-Encoding",
    "Accept-Language",
    "Accept-Datetime",
    "Authorization",
    "Cache-Control",
    "Connection",
    "Cookie",
    "Content-Length",
    "Content-MD5",
    "Content-Type",
    "Date",
    "Expect",
    "From",
    "Host",
    "If-Match",
    "If-Modified-Since",
    "If-None-Match",
    "If-Range",
    "Max-Forwards",
    "Origin",
    "Pragma",
    "Proxy-Authorization",
    "Range",
    "Referer",
    "TE",
    "Upgrade",
    "User-Agent",
    "Via",
    "Warning"]

#http://www.w3.org/Protocols/rfc2616/rfc2616-sec14.html

HEADERS_RESPONSE = [
    "Access-Control-Allow-Origin",
    "Accept-Ranges",
    "Age",
    "Cache-Control",
    "Connection",
    "Content-Encoding",
    "Content-Language",
    "Content-Length",
    "Content-Location",
    "Content-MD5",
    "Content-Disposition",
    "Content-Range",
    "Content-Type",
    "Date",
    "ETag",
    "Expires",
    "Last-Modified",
    "Link",
    "Location",
    "P3P",
    "Pragma",
    "Proxy-Authenticate",
    "Refresh",
    "Retry-After",
    "Server",
    "Set-Cookie",
    "Status",
    "Strict-Transport-Security",
    "Trailer",
    "Transfer-Encoding",
    "Vary",
    "Via",
    "Warning",
    "WWW-Authenticate",
    "X-Type",
    "X-Handler"]

HTTP_STATUS = {
    100: "Continue",
    101: "Switching Protocols",
    102: "Processing",
    200: "OK",
    201: "Created",
    202: "Accepted",
    203: "Non-Authoritative Information",
    204: "No Content",
    205: "Reset Content",
    206: "Partial Content",
    207: "Multi-Status",
    208: "Already Reported",
    226: "IM Used",
    300: "Multiple Choices",
    301: "Moved Permanently",
    302: "Found",
    303: "See Other",
    304: "Not Modified",
    305: "Use Proxy",
    306: "Switch Proxy",
    307: "Temporary Redirect",
    308: "Permanent Redirect",
    400: "Bad Request",
    401: "Unauthorized",
    402: "Payment Required",
    403: "Forbidden",
    404: "Not Found",
    405: "Method Not Allowed",
    406: "Not Acceptable",
    407: "Proxy Authentication Required",
    408: "Request Timeout",
    409: "Conflict",
    410: "Gone",
    411: "Length Required",
    412: "Precondition Failed",
    413: "Request Entity Too Large",
    414: "Request-URI Too Long",
    415: "Unsupported Media Type",
    416: "Requested Range Not Satisfiable",
    417: "Expectation Failed",
    418: "I'm a teapot",
    422: "Unprocessable Entity",
    423: "Locked",
    424: "Failed Dependency",
    424: "Method Failure",
    425: "Unordered Collection",
    426: "Upgrade Required",
    428: "Precondition Required",
    429: "Too Many Requests",
    431: "Request Header Fields Too Large",
    449: "Retry With",
    450: "Blocked by Windows Parental Controls",
    451: "Unavailable For Legal Reasons",
    500: "Internal Server Error",
    501: "Not Implemented",
    502: "Bad Gateway",
    503: "Service Unavailable",
    504: "Gateway Timeout",
    505: "HTTP Version Not Supported",
    506: "Variant Also Negotiates",
    507: "Insufficient Storage",
    508: "Loop Detected",
    509: "Bandwidth Limit Exceeded",
    510: "Not Extended",
    511: "Network Authentication Required",
    598: "Network read timeout error",
    599: "Network connect timeout error"}

ENVIRON_TEST = {'PATH_INFO':'/',
                'REQUEST_METHOD':'GET',
                'QUERY_STRING':'',
                'HTTP_ACCEPT':'*/*'}