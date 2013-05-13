#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#

__all__ = ['WebgetTool']


import unittest
import doctest
import sys
import os
import urllib2
import codecs

from xnet.tools import Tool
#from xnet.debug import pdb


class WebgetException(Exception):
    pass


class WebgetTool(Tool):

    __toolname__ = 'webget'
    __itemname__ = 'url'
    __description__ = 'get information from web services'

    cmdline_options = [
        ('-s', '--server', 'print server header',
            dict(dest='server', action='store_true')),
        ('-S', '--https', 'default to https when protocol is missing',
            dict(dest='https', action='store_true')),
        ('', '--host', 'specify Host header manually',
            dict(dest='host')),
        ('', '--proxy', 'use this proxy for all protocols',
            dict(dest='proxy')),
        ('', '--code', 'only print response code',
            dict(dest='code', action='store_true')),
        ('', '--xpath', 'grab elements matching xpath expression',
            dict(action='append', metavar='expr')),
        ('', '--xpath-delimiter', 'xpath output delimiter when using multiple --xpath\'s',
            dict(dest='xpath_delimiter', action='store_true')),
        ('', '--xpath-strict', 'exit if not all --xpath\'s are matched',
            dict(dest='xpath_strict', action='store_true')),
    ]

    @classmethod
    def print_source(cls):
        cls._print_source(__file__)

    def __init__(self, *args, **kw):
        super(WebgetTool, self).__init__(*args, **kw)
        self._url = None

    def __parse__(self, line, iterator):
        '''
            only accepts plain urls atm.
        '''
        result = {}
        self._url = url = line.strip()
        if not '://' in url:
            proto = 'http'
            if self.options.https:
                proto = 'https'
            url = proto + '://' + url
        result['url'] = url
        result['host'] = self.options.host or self._get_host(url)
        return result

    def _get_host(self, url):
        host = url.split('://', 1)[1]
        if '/' in host:
            host = host.split('/', 1)[0]
        return host

    def __action__(self, parse_result):
        result = {}
        _host = parse_result['host']
        _url = parse_result['url']
        _response = None
        _body_unicode = None
        _code = None
        _msg = None
        _body = None
        #
        #proxies = {}
        #
        request_kwargs = {}
        request_kwargs['url'] = _url
        if self.options.host:
            request_kwargs['headers'] = {'Host': self.options.host}
            _host = self.options.host
        request = urllib2.Request(**request_kwargs)
        #
        # FIXME: broken with proto mismatches etc.
        #
        if self.options.proxy:
            if _url.startswith('http://'):
                request.set_proxy(self.options.proxy, 'http')
            elif _url.startswith('https://'):
                request.set_proxy(self.options.proxy, 'http')
            else:
                errmsg = 'invalid url prefix: ' + _url
                raise WebgetException(errmsg)
            #request.set_proxy(self.options.proxy, 'https')

        read_response = not self.options.code \
                        and not self.options.server

        if self.options.format and '{body}' in self.options.format:
            read_response = True

        try:
            _response = urllib2.urlopen(request)
            self._register_cleanup(lambda: _response.close())
            _code = _response.code
            _msg = _response.msg
            if read_response:
                _body = _response.read()
        except urllib2.HTTPError, e:
            _response = None
            _code = e.code
            _msg = e.msg
            if read_response:
                _body = e.read()
        except urllib2.URLError, e:
            errmsg = _url + ' '
            if type(e.reason) is str:
                errmsg += e.reason.replace(' ', '-').replace(',', '-')
            else:
                errmsg += e.reason.strerror.replace(' ', '-').replace(',', '-')
            self.set_error(errmsg)
            self.stderr = True
            return None
        #except:
        #    e = str(sys.exc_info())
        #    self.set_error(e)
        #    self.stderr = True
        #    return None
        finally:
            try:
                _response.close()
            except:
                pass
        if not _response:
            return None
        content_type = _response.headers.get('content-type', None)
        charset = None
        if content_type:
            w = content_type.split(';')
            content_type = w[0]
            for s in w[1:]:
                s = s.strip()
                if s.startswith('charset='):
                    charset = s.split('charset=', 1)[1]
        if charset:
            _body_unicode = codecs.decode(_body, charset)
        else:
            _body_unicode = codecs.decode(_body, 'Latin-1')
            #_body_unicode = unicode(_body)
            
        result['host'] = _host
        result['url'] = _url
        result['response'] = _response
        result['code'] = _code
        result['msg'] = _msg
        result['body'] = _body
        result['body_unicode'] = _body_unicode
        return result

    def __format__(self, line, parse_result, action_result):
        options = self.options
        url = action_result['url']
        response = action_result['response']
        code = action_result['code']
        msg = action_result['msg']
        output = ''
        #
        if options.server:
            server = response.headers.get('server', None)
            output = '{0} {1}'.format(url, server)
        elif options.code:
            if options.verbose:
                output = '{0} {1} {2}'.format(url, code, msg)
            else:
                output = '{0} {1}'.format(url, code)
        elif options.xpath:
            try:
                import lxml.etree
            except ImportError:
                import time
                errmsg = '\n'
                errmsg += '*** XNET USAGE INFORMATION ***\n'
                errmsg += '\n'
                errmsg += 'ImportError raised, lxml.etree might be missing.\n'
                errmsg += 'For Debian, try:\n'
                errmsg += '  $ sudo apt-get install python-lxml\n'
                errmsg += 'For OSX, try:\n'
                errmsg += '  $ sudo port install py-lxml\n'
                print errmsg
                time.sleep(3)
                raise
            htmlparser = lxml.etree.HTMLParser()
            tree = lxml.etree.fromstring(action_result['body_unicode'], htmlparser)
            for xpath in self.options.xpath:
                xpath_result = tree.xpath(xpath)
                success = False
                for elem in xpath_result:
                    success = True 
                    if type(elem) is lxml.etree._ElementStringResult:
                        elem = str(elem)
                    if not type(elem) is str:
                        elem = lxml.etree.tostring(elem)
                    output += elem
                    if len(output) and output[-1] != '\n':
                        output += '\n'
                if self.options.xpath_strict and not success:
                    import tempfile
                    (fd, name) = tempfile.mkstemp(prefix='webget-xpath-fail-')
                    os.write(fd, action_result['body'])
                    os.close(fd)
                    msg = 'Error: XPath not matched: {0}'.format(xpath)
                    msg += ', body saved to {0}'.format(name)
                    sys.exit(msg)
                output += self.options.xpath_delimiter or ' '
        else:
            output = action_result['body']
        return output

    @classmethod
    def __format_help__(cls):
        output = '''
Format variables for %s:

 host     - target host
 url      - target URL
 code     - status code
 msg      - status message
 body     - response body

Default format depend on commandline arguments.
        ''' % cls.__toolname__
        return output

    def __timeout__(self):
        return 'timeout {0}\n'.format(self._url)


def main():
    import xnet.tools.run
    xnet.tools.run.run(WebgetTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
