#!/usr/bin/env python
#
# Copyright 2013-2014 Sergio Arroutbi Braojos <sarroutbi@yahoo.es>
# 
# Permission to use, copy, modify, and/or distribute this software 
# for any purpose with or without fee is hereby granted, provided that 
# the above copyright notice and this permission notice appear in all copies.
# 
# THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES 
# WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY 
# AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, 
# INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM 
# LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, 
# NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH 
# THE USE OR PERFORMANCE OF THIS SOFTWARE
#
from urllib2 import build_opener, URLError, HTTPError
from bs4 import BeautifulSoup as Soup

def url_to_string(url):
    """ 
    This functions returns the text of the page specified by url parameter
   
    Keyword arguments:
    url -- a URL whose text will be returned

    """
    try:
        opened = build_opener()
        # Get the string 
        string = opened.open(url).read()
    except (URLError, HTTPError, ValueError):
        return ""
    return string

def get_url_list(html_text):
    """ 
    This functions returns a list with all the links of type
    <a href="http://whatever">whatever</a> contained
   
    Keyword arguments:
    html_text -- HTML text where <a href="http://whatever">whatever</a>
                 links will be searched

    """
    text = url_to_string(html_text)
    try:
        s = Soup(text)
        return [x['href'] for x in s.findAll('a', href=True)]
    except:
        print "ERROR ON SOUP CREATION"
        return []
