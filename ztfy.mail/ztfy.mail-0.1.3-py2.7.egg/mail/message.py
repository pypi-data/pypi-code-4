### -*- coding: utf-8 -*- ####################################################
##############################################################################
#
# Copyright (c) 2012 Thierry Florac <tflorac AT ulthar.net>
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


# import standard packages
from cStringIO import StringIO
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

import chardet
import codecs
import htmllib, htmlentitydefs, formatter

# import Zope3 interfaces

# import local interfaces

# import Zope3 packages

# import local packages
from ztfy.utils.timezone import gmtime


def htmlReplace(exc):
    if isinstance(exc, (UnicodeEncodeError, UnicodeTranslateError)):
        s = [ u'&%s;' % htmlentitydefs.codepoint2name[ord(c)] for c in exc.objet[exc.start:exc.end] ]
        return ''.join(s), exc.end
    else:
        raise TypeError("Can't handle exception %s" % exc.__name__)
codecs.register_error('html_replace', htmlReplace)


def htmlEncode(unicode_data, encoding='utf-8'):
    return unicode_data.encode(encoding, 'html_replace')


def HTMLMessage(subject, fromaddr, toaddr, html, text=None):
    """Create a MIME message that will render as HTML or text
    
    Copied from 'Python Cookbook', chapter 13.5"""
    html = htmlEncode(html)
    if text is None:
        # produce textual rendering of the HTML string when None is provided
        textout = StringIO()
        formtext = formatter.AbstractFormatter(formatter.DumbWriter(textout))
        parser = htmllib.HTMLParser(formtext)
        parser.feed(html)
        parser.close()
        text = textout.getvalue()
        del textout, formtext, parser
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['Date'] = gmtime(datetime.utcnow()).strftime('%a, %d %b %Y %H:%M:%S %z (%Z)')
    msg['From'] = fromaddr
    if isinstance(toaddr, (str, unicode)):
        toaddr = (toaddr,)
    msg['To'] = ', '.join(toaddr)
    parts = MIMEMultipart('alternative')
    plain_part = MIMEText(text, 'plain')
    plain_part.set_charset('utf-8')
    html_part = MIMEText(html, 'html')
    html_part.set_charset('utf-8')
    parts.attach(plain_part)
    parts.attach(html_part)
    msg.attach(parts)
    return msg


def TextMessage(subject, fromaddr, toaddr, text):
    """Create a text message"""
    msg = MIMEMultipart()
    msg['Subject'] = subject
    msg['Date'] = gmtime(datetime.utcnow()).strftime('%a, %d %b %Y %H:%M:%S %z (%Z)')
    msg['From'] = fromaddr
    if isinstance(toaddr, (str, unicode)):
        toaddr = (toaddr,)
    msg['To'] = ', '.join(toaddr)
    charset = chardet.detect(text).get('encoding', 'utf-8')
    plain_part = MIMEText(text, 'plain', charset)
    msg.attach(plain_part)
    return msg
