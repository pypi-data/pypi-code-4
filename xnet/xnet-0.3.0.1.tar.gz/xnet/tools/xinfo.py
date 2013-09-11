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


__all__ = ['XInfoTool']


import sys
import os
import codecs
import urlparse

from xnet.tools import Tool
from xnet.net.ipv4 import PortRangeIterator
from xnet.net.http import UrlIterator
#from xnet.debug import pdb
import xnet.packages.urllib3
import xnet.packages.urllib3.exceptions


class XInfoException(Exception):
    pass


class XInfoTool(Tool):

    __toolname__ = 'xinfo'
    __itemname__ = 'url'
    __description__ = 'get information from various external sources'

    cmdline_options = [
        ('', '--tag-lines', 'prefix each line with current url',
            dict(dest='tag_lines', action='store_true')),
    ]

    @classmethod
    def print_source(cls):
        cls._print_source(__file__)

    MAX_REDIRECTS = 8

    def __init__(self, *args, **kw):
        super(XInfoTool, self).__init__(*args, **kw)
        if not hasattr(self, '_http'):
            self._http = self.__class__._http = self._get_connection()
        raise Exception('Work in progress')

    def _get_connection(self):
        return xnet.packages.urllib3.PoolManager()

    def _request(self, *args, **kw):
        result = None
        done = False
        while not done:
            try:
                result = self._http.request(*args, **kw)
            except xnet.packages.urllib3.exceptions.ClosedPoolError:
                pass  # urllib3 seems to take care of this
            else:
                done = True
        return result

    def __parse__(self, ip, iterator):
        url = url.strip()
        result = {'url': url}
        return result

    def _get_host(self, url):
        return urlparse.urlparse(url).netloc

    def __action__(self, parse_result):
        result = {}
        _url = self._url = parse_result['url']
        _host = self.options.host or self._get_host(_url)
        _method = self.options.method or 'GET'
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
        import pdb; pdb.set_trace() ### XXX BREAKPOINT

        if self.options.host:
            request_kwargs['headers'] = {'Host': self.options.host}
            _host = self.options.host

        read_response = not self.options.code \
            and not self.options.server

        if self.options.format and '{body}' in self.options.format:
            read_response = True

        done = False
        redirect_count = 0
        #
        # loop to handle redirects
        #
        while not done:
            try:
                _response = self._request(_method, _url, **request_kwargs)
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

                    if ourl.scheme.lower() == 'http' and lurl.scheme.lower() == 'https':
                        #
                        # Allow http to https but nothing else.
                        #
                        pass
                    elif lurl.scheme and lurl.scheme.lower() != ourl.scheme.lower():
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
            _body_unicode = codecs.decode(_body, 'Latin-1', 'ignore')
            #_body_unicode = unicode(_body)

        if read_response and self.options.tag_lines:
            tag = self._url + ':'
            _body = '\n' + tag + _body.replace('\n', '\n' + tag)

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

Default format depend on commandline arguments.
        ''' % cls.__toolname__
        return output

    def __timeout__(self):
        return 'timeout {0}\n'.format(self._url)


def main():
    import xnet.tools.run
    xnet.tools.run.run(XInfoTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
