#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import re, formv
from pkg_resources import resource_filename as rn   #@UnresolvedImport #pylint: disable=E0611
from gettext import translation
from formv.utils.compat import PY2, PY3

extract_text = lambda s: s

class dict_object(dict):    
    def __getattr__(self, k):        
        try:
            return self[k]        
        except KeyError:            
            raise AttributeError(k)
            
    def __setattr__(self, k, v):        
        self[k] = v


def empty(value):
    return value in (None,[],(),{},'',)


def install_language(domain="formv", languages=None, 
                     localedir=None, codeset='utf-8'):
    if localedir is None:
        localedir = rn('formv', 'config/i18n')
    t = translation(domain=domain, localedir=localedir,
                    languages=languages, codeset=codeset,
                    fallback=True)
    if PY2:
        formv.translate = t.ugettext
    if PY3:
        formv.translate = t.gettext
    t.install()
install_language()


def match(formats, value):
    """
    Used to match phone numbers, postcodes,...
        
        * = any alphanumeric character (\w)
        @ = [a-zA-Z]_
        # = [0-9]   
        
        Example:
            phone format: +1 #### ####
            postcode format: ####, *####/####, @@# ###         
    """    
    specials = ('`~!@#$%^&*()_-+={}[];:"\'<>,.?/|')
    
    for f in formats:   
        if len(f) == len(value):
            f = ' '.join(f.split())  
            f = f.replace('\\','\\\\').replace(' ', '\s')
            f = f.replace('@','[a-zA-Z]').replace('#','\d').replace('*','\w')                   
            for c in specials:
                f = f.replace(c,'\\'+c)        
            m = re.compile(f)
            if m.search(value):
                return value
    raise ValueError('Format not matched')

