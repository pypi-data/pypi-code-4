#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#
# Known bugs:
#   Debian Squeeze, apt-get:ed python-gevent
#       * some DNS queries for nonexistent hosts
#         are not cancelled by -w, but takes a long time to complete.
#


__all__ = ['WebgetTool']


import unittest
import doctest
import sys
import os
import codecs
import urlparse

from xnet.tools import Tool
#from xnet.debug import pdb
import xnet.packages.urllib3
import xnet.packages.urllib3.exceptions


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
        ('', '--redirect-allow-samedomain', 'follow redirects under the same domain',
            dict(dest='redirect_allow_samedomain', action='store_true')),
        ('', '--redirect-whitelist', 'comma-separated whitelist of allowed redirect hosts',
            dict(dest='redirect_whitelist', metavar='hosts')),
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

    MAX_REDIRECTS = 8

    def __init__(self, *args, **kw):
        super(WebgetTool, self).__init__(*args, **kw)
        if not hasattr(self, '_http'):
            self._http = self.__class__._http = \
                xnet.packages.urllib3.PoolManager()
        self._url = None
        self._redirect_whitelist = set()
        if self.options.redirect_whitelist:
            allowed_hosts = self.options.redirect_whitelist.split(',')
            allowed_hosts = [h.lower() for h in allowed_hosts]
            self._redirect_whitelist = set(allowed_hosts)

    def _request(self, *args, **kw):
        result = None
        done = False
        while not done:
            try:
                result = self._http.request(*args, **kw)
            except xnet.packages.urllib3.exceptions.ClosedPoolError:
                pass
            else:
                done = True
        return result


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

    def _explicitly_allowed_redirect(self, ourl, lurl):
        if lurl.netloc.lower() in self._redirect_whitelist:
            return True
        if self.options.redirect_allow_samedomain:
            if not lurl.scheme and not lurl.netloc:
                return True
            ow = ourl.netloc.lower().split('.')
            lw = lurl.netloc.lower().split('.')
            if len(ow) > 1 and len(lw) > 1:
                if not ow[-1].isdigit():
                    if ow[-2:] == lw[-2:]:
                        return True
        return False

    def __action__(self, parse_result):
        result = {}
        _host = parse_result['host']
        _url = parse_result['url']
        _response = None
        _body_unicode = None
        _code = None
        _msg = None
        _body = ''
        #
        #proxies = {}
        #
        request_kwargs = {}
        request_kwargs['redirect'] = False

        if self.options.host:
            request_kwargs['headers'] = {'Host': self.options.host}
            _host = self.options.host

        read_response = not self.options.code \
            and not self.options.server

        import pdb; pdb.set_trace() ### XXX BREAKPOINT
        if self.options.format and '{body}' in self.options.format:
            read_response = True


        done = False
        redirect_count = 0
        #
        # loop to handle redirects
        #
        while not done:
            try:
                _response = self._request('GET', _url, **request_kwargs)
            except xnet.tools.WaitTimeout:
                raise
            except xnet.packages.urllib3.exceptions.MaxRetryError, e:
                if e.reason and e.reason.strerror:
                    self.set_error(e.reason.strerror, oneword=True)
                else:
                    self.set_error(e)
                return None
            except:
                import traceback
                print  traceback.print_exc(sys.exc_info()[1])
                e = str(sys.exc_info())
                self.set_error(e)
                self.stderr = True
                return None

            _code = _response.status
            _msg = _response.reason

            if not _code in [301, 302, 303, 307]:
                done = True
            else:
                if redirect_count == self.MAX_REDIRECTS:
                    self.set_error('redirect-limit-reached')
                    return None
                redirect_count += 1

                location = _response.getheaders().get('location', None)
                if location is None or location.strip() == '':
                    self.set_error('redirect-empty-location')
                    return None
                ourl = urlparse.urlparse(_url)
                lurl = urlparse.urlparse(location)

                if (lurl.scheme == '' or lurl.scheme == ourl.scheme) \
                        and (lurl.netloc == '' or lurl.netloc == ourl.netloc) \
                        and lurl.path == ourl.path:
                    self.set_error('redirect-loop')
                    return None

                if not self._explicitly_allowed_redirect(ourl, lurl):
                    if lurl.netloc and lurl.netloc.lower() != ourl.netloc.lower():
                        msg = 'redirect-host-mismatch {0}'.format(location)
                        self.set_error(msg)
                        return None

                    if lurl.scheme and lurl.scheme.lower() != ourl.scheme.lower():
                        msg = 'redirect-host-mismatch {0}'.format(location)
                        self.set_error(msg)
                        return None

                #
                # Create new url by updating path, query and fragment.
                #
                scheme, netloc, path, query, fragment = \
                    urlparse.urlsplit(_url)
                parts = (
                    lurl.scheme or scheme,
                    lurl.netloc or netloc,
                    lurl.path,
                    lurl.query,
                    lurl.fragment
                )
                _url = urlparse.urlunsplit(parts)

        if read_response:
            _body = _response.data

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
            _body_unicode = codecs.decode(_body, charset, 'ignore')
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
