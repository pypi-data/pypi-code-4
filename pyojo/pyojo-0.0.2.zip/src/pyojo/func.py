# -*- coding: utf-8 -*-
# ----------------------------------------------------------------------------
# pyojo                                           Copyright (c) 2011 nabla.net
# ----------------------------------------------------------------------------
""" Collection of package wide utilities.
"""
import os
import re
import sys
import cgi
import imp
import time
import datetime
import json
import pprint
import logging
import urllib2
from urlparse import parse_qs
from urllib import urlencode

import StringIO

#----------------------------------------------------------------------------
#--- Constants

LF = "\n"
ENCODING = 'utf-8'
XML_VER = '<?xml version="1.0" encoding="'+ENCODING+'"?>'
DTD_VER = '-//W3C//DTD HTML 4.01 Transitional//EN'
DTD_URL = 'http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd'
DOCTYPE = '<!DOCTYPE html PUBLIC "'+DTD_VER+'" "'+DTD_URL+'" >'

#----------------------------------------------------------------------------
#--- Logging

def timestamp(timer=None, format="%Y-%m-%d %H:%M:%S"):
    if timer is None: timer = time.time()
    dt_obj = datetime.datetime.fromtimestamp(timer)
    return dt_obj.strftime(format)


if not os.path.exists("log"): os.makedirs("log")

LOG = os.path.join(os.getcwd(), "log",
                    'pyojo-'+timestamp(format="%y%m%d-%H%M%S")+'.log')

logging.basicConfig(filename=LOG, 
                format='%(levelname)s:%(message)s', 
                level=logging.DEBUG)



# create main logger
log = logging.getLogger('pyojo')
log.setLevel(logging.DEBUG)

# create console handler and set level to debug
_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
_ch = logging.StreamHandler()
_ch.setLevel(logging.DEBUG)
_ch.setFormatter(_formatter)
log.addHandler(_ch)


try:
    import jsbeautifier
    from jsbeautifier import beautify as jsbeautify
    jsb_opts = jsbeautifier.default_options()
    jsb_opts.keep_array_indentation = True
except:
    log.warning("Module jsbeautifier not installed.")
    jsbeautify = None
    jsb_opts = None

#----------------------------------------------------------------------------
#--- Functions


def template_to_regex(template):
    var_regex = re.compile(r'''
    \{          # The exact character "{"
    (\w+)       # The variable name (restricted to a-z, 0-9, _)
    (?::([^}]+))? # The optional :regex part
    \}          # The exact character "}"
    ''', re.VERBOSE)
    regex = ''
    last_pos = 0
    for match in var_regex.finditer(template):
        regex += re.escape(template[last_pos:match.start()])
        var_name = match.group(1)
        expr = match.group(2) or '[^/]+'
        expr = '(?P<%s>%s)' % (var_name, expr)
        regex += expr
        last_pos = match.end()
    regex += re.escape(template[last_pos:])
    regex = '^%s$' % regex
    return regex

def escape(text):
    #text = text.replace("'", "/'")
    return re.escape(text)

_PrettyPrinter = pprint.PrettyPrinter(indent=4)

def pretty(text):
    """ Format the text to better readability.
    """
    #_PrettyPrinter.pprint(text)
    return _PrettyPrinter.pformat(text)

def html_escape(text):
    return cgi.escape(text)

def raw_str(string):
    if isinstance(string, str):
        string = string.encode('string-escape')
    elif isinstance(string, unicode):
        string = string.encode('unicode-escape')
    else:
        raise Error("raw_str(%s)" % type(string))
    return string#.replace("'", "\'").replace('"', '\"')

def http_request_headers(environ):
    """ Returns only the HTTP items of environ.
    """
    e = {}
    for key,value in environ.iteritems():
        if not os.environ.has_key(key):
            e[key]=value
    return e


def accepts(offered, accepted):
    """ Check if Content-Type fits.
    """
    def fits(cta, ctb):
        if cta == "*" or ctb == "*": 
            return True
        return cta == ctb
    offer = offered.split("/")
    accepted = accepted.split(";")[0]
    
    for each in accepted.split(","):
        accept = each.split("/")
        if fits(offer[0], accept[0]) and fits(offer[1], accept[1]): 
            return True
    return False
#----------------------------------------------------------------------------
#--- IMPORTS

def import_url(path, url):
    """ Import a module from a file.
    """
    mod = "_".join(url.rsplit(".", 1))
    if "/" in mod:
        folder, name = mod.rsplit("/",1)
    else:
        folder, name = "", mod

    mod_name = "mod" + folder.replace("/", "_") + "_" + name
    if folder.startswith("/"): 
        folder = folder[1:]
    mod_folder = folder.replace("/", os.path.sep)
    mod_path = os.path.join(path, mod_folder)
    #print "Buscando %s %s en %s" % (mod_folder, name, mod_path)
    try:
        file_obj, filename, data = imp.find_module(name, [mod_path])
    except ImportError, ex:
        raise ModuleNotFoundError(url, ex)
    
    #print "Modulo %s cargado de %s" % (mod_name, filename)
    return imp.load_module(mod_name, file_obj, filename, data)


def import_call(name, module="pyojo.call"):
    
    fullname = module+"."+name
    try:
        mod = __import__(fullname)
    except ImportError, e:
        parts = name.split(".")
        subd = os.path.sep.join(parts[0:-1])
        path = os.path.join(Config.path, "call", subd)
        try:
            imp.find_module(parts[-1], [path])
        except ImportError, e:
            raise ModuleNotFoundError(fullname, e) #

    components = fullname.split('.')
    for comp in components[1:]:
        mod = getattr(mod, comp)
    return mod




def import_path(path, name):
    """ Import a module from a file. 
    
        :raises:
            ``pyojo.ModuleNotFoundError`` if module is not found.
    """        
    if name in dir(sys.modules[globals()['__name__']]):
        print "Reloading module '%s'" % name
        reload(sys.modules[name])
    parts = name.split(".")
    subd = os.path.sep.join(parts[0:-1])
    path = os.path.join(path, "call", subd)
    print "Searchig %s in %s" % (parts[-1], path)
    try:
        file, filename, data = imp.find_module(parts[-1], [path])
    except ImportError, e:
        log.warning("Module %s not found at %s", name, path)
        raise ModuleNotFoundError(name, e) #
    log.debug("Module %s loaded from %s", name, filename)
    return imp.load_module(name, file, filename, data)



def nolf(text):
    lines = []
    for line in text.split("\n"):
        lines.append(line.lstrip().rstrip())
    text = "".join(lines)
    return text.replace("\n", "")



def indent(text, i=1):
    """ Add indentation to a string.
    """
    lines = []
    for line in text.split("\n"):
        lines.append(" "*i+line)
    return "\n".join(lines)


    
def tmpl_replace(template, *kwargs):
    """ Replace node text.
    
        Pass the template and a named parameter for each desired replacement.
    """
    for find, replace in kwargs:
        template = template.replace('__'+find+'__', replace) 
    return template



def html_highlighter(code, lang="javascript"):
    """ Highlight a code.
    """
    page = """<html><head>
    <script type="text/javascript" src="/static/js/shjs/sh_main.min.js"></script>
    <script type="text/javascript" src="/static/js/shjs/lang/sh_%s.min.js"></script>
    <link type="text/css" rel="stylesheet" href="/static/js/shjs/css/sh_darkness.min.css">
    </head><body bgcolor='#000000' onload="sh_highlightDocument();">
    <pre class="sh_%s">
    %s
    </pre></body></html>"""
    return page % (lang, lang, code)
    
    
def subclasses(supercls):
    """ Get all known subclasses.
    """
    found = []
    for cls in supercls.__subclasses__():
        found.append(cls)
        if len(cls.__subclasses__()) > 0:
            found.extend(subclasses(cls))
    return found
        
        
def browse(url=None, method="GET", content="*/*"):
    """ Testing browser.
    """
    request = urllib2.Request(url=url,
                              headers={'Content-Type':content}, 
                              #data=data
                              )
    reply = urllib2.urlopen(request)
    return reply.read()


class Decorator(object): 
    """ A object that can customize a callable.
    
        Nothing more.
    """
    pass


        
#----------------------------------------------------------------------------
#--- ERRORS

class Error(Exception):
    """ Base class for specific pyojo known errors.
    """
    def __init__(self, value):
            self.value = value
    def __str__(self):
        return repr(self.value)


class DataError(Error):
    """ Exception at the data operation.
    """
    def __init__(self, data, e):
        self.data = data
        self.e = e
        
    def __str__(self):
        return self.e+" (%s %s)" % (type(self.data).__name__, 
                                    self.data)


class ResponseNotImplemented(Error):
    """ The response is not available.
    """
    def __init__(self, obj, e):
        self.obj = obj
        self.e = e
        
    def __str__(self):
        return +"%s (%s)" % (self.e, self.obj)

class ModuleNotFoundError(Error):
    """ The module can not be loaded.
    """
    def __init__(self, module, e):
        self.module = module
        self.e = e
        
    def __str__(self):
        return self.module+"(%s)" % self.e



#----------------------------------------------------------------------------