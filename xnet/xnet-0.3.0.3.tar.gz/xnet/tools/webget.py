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


#import unittest
#import doctest
import sys
import codecs
import urlparse

from xnet.tools import Tool
from xnet.net.ipv4 import PortRangeIterator
from xnet.net.http import UrlIterator
from xnet.net.http import HTMLParser
from xnet.net.http import HTMLParserException
#from xnet.tools import ToolMixin_AddrIterator
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
        ('-p', '--ports', 'use these ports for urls lacking port AND protocol components',
            dict(dest='ports', metavar='m-n,..')),
        ('-s', '--server', 'print server header',
            dict(dest='server', action='store_true')),
        ('-S', '--https', 'default to https when protocol is missing',
            dict(dest='https', action='store_true')),
        ('', '--host', 'specify Host header manually',
            dict(dest='host')),
        ('', '--method', 'specify alternative method. Examples GET, HEAD, POST, ...',
            dict(dest='method', metavar='method')),
        ('', '--proxy', 'broken, sorry!',
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
            dict(dest='xpath_delimiter', default='\n', metavar='delim')),
        ('', '--xpath-strict', 'exit if not all --xpath\'s are matched',
            dict(dest='xpath_strict', action='store_true')),
        ('', '--tag-lines', 'prefix each line with current url',
            dict(dest='tag_lines', action='store_true')),
    ]

    @classmethod
    def print_source(cls):
        cls._print_source(__file__)

    MAX_REDIRECTS = 8

    def __init__(self, *args, **kw):
        super(WebgetTool, self).__init__(*args, **kw)
        if self.options.proxy:
            msg = '--proxy is broken atm, sorry!'
            raise Exception(msg)
        if not hasattr(self, '_http'):
            self._http = self.__class__._http = self._get_connection()
        self._url = None
        self._redirect_whitelist = set()
        if self.options.redirect_whitelist:
            allowed_hosts = self.options.redirect_whitelist.split(',')
            allowed_hosts = [h.lower() for h in allowed_hosts]
            self._redirect_whitelist = set(allowed_hosts)

    def _get_connection(self):
        if self.options.proxy:
            return xnet.packages.urllib3.proxy_from_url(self.options.proxy)
        else:
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

    @classmethod
    def __massage__(cls, iterator, options):
        default_scheme = 'http'
        default_ports = [80]
        if options.https:
            default_scheme = 'https'
            default_ports = [443]
        if options.ports:
            default_ports = list(PortRangeIterator(options.ports))
        urlIterator = UrlIterator(default_scheme=default_scheme, default_ports=default_ports)
        for xurl in iterator:
            for url in urlIterator.expand(xurl):
                yield url

    def __parse__(self, url, iterator):
        url = url.strip()
        result = {}
        result['url'] = url
        result['host'] = self._get_host(url)
        return result

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
        _xpath_result = None
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
                if hasattr(e, 'reason') and e.reason:
                    if hasattr(e.reason, 'strerror'):
                        self.set_error(e.reason.strerror)
                    else:
                        self.set_error(e.reason)
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

            #
            # Should we care about other redirect codes than these?
            #
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
                from_url = _url
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
                self.vprint_stderr(1, '[*] follow redirect {0} => {1}\n'.format(
                    from_url, _url
                ))

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
            try:
                _body_unicode = codecs.decode(_body, charset, 'ignore')
            except LookupError, e:
                self.vprint_stderr(1, str(e), ', attempting utf-8\n')
                try:
                    _body_unicode = codecs.decode(_body, 'utf-8', 'ignore')
                except:
                    e = sys.exc_info()
                    self.set_error(e[1])
                    return None
        else:
            self.vprint_stderr(1, '[*] Defaulting to charset utf-8: {0}\n'.format(_url))
            _body_unicode = codecs.decode(_body, 'utf-8', 'ignore')
            #_body_unicode = codecs.decode(_body, 'Latin-1', 'ignore')
            #_body_unicode = unicode(_body)

        if self.options.xpath:
            try:
                htmlparser = HTMLParser(_body_unicode)
            except HTMLParserException, e:
                self.set_error(e)
                return None
            _xpath_result = ''
            for xpath in self.options.xpath:
                if len(_xpath_result):
                    _xpath_result += '\n'
                _xpath_result += htmlparser.xpath(xpath,
                                                  match_delimiter=self.options.xpath_delimiter)

        if read_response and hasattr(self.options, 'tag_lines') and self.options.tag_lines:
            #tag = self._url + ':'
            #_body = '\n' + tag + _body.replace('\n', '\n' + tag)
            tag = '\n' + self._url + ':'
            _body = tag + tag.join(_body.split('\n'))

        result['host'] = _host
        result['url'] = _url
        result['response'] = _response
        result['server'] = _response.headers.get('server', None)
        result['code'] = _code
        result['msg'] = _msg
        result['body'] = _body
        result['body_unicode'] = _body_unicode
        result['xpath_result'] = _xpath_result
        return result

    def __format__(self, line, parse_result, action_result):
        options = self.options
        url = action_result['url']
        #response = action_result['response']
        server = action_result['server']
        code = action_result['code']
        msg = action_result['msg']
        output = ''
        #
        # alert if used together!
        #
        if options.server:
            output = '{0} {1}'.format(url, server)
        elif options.code:
            if options.verbose:
                output = '{0} {1} {2}'.format(url, code, msg)
            else:
                output = '{0} {1}'.format(url, code)
        elif options.xpath:
            output = action_result['xpath_result']
            if 0:
                try:
                    htmlparser = HTMLParser(action_result['body_unicode'])
                except HTMLParserException, e:
                    self.set_error(e)
                xpath_result = ''
                for xpath in self.options.xpath:
                    if len(xpath_result):
                        xpath_result += '\n'
                    xpath_result += htmlparser.xpath(xpath,
                                                     match_delimiter=self.options.xpath_delimiter)
                output = xpath_result
        else:
            output = action_result['body']
        return output

    @classmethod
    def __format_help__(cls):
        output = '''
Format variables for %s:

 host         - target host
 url          - target URL
 server       - Server header value
 code         - status code
 msg          - status message
 body         - response body
 xpath_result - results from xpath evaluation
 time         - time consumed by action, in ms
 pid          - PID of executing process
 grid         - Greenlet ID of executing process

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
