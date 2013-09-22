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
from urlparse import urlparse 

def url_is_http(url):
    """ 
    This functions checks if url has HTTP/HTTPS scheme 
   
    Keyword arguments:
    url -- A string with the URL to analyze

    """
    parsed = urlparse(url)
    if parsed.scheme and \
        (parsed.scheme == 'http' or parsed.scheme == 'https'):
        return True
    return False
