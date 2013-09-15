#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright(c) 2013 Krister Hedfors
#
#i = "hälp me"
#i = unicode(i.decode("iso-8859-4"))


__all__ = ['SeleniumTool']


#import unittest
#import doctest
import sys
import os
import codecs
import urlparse

from xnet.tools import Tool
from xnet.net.ipv4 import PortRangeIterator
from xnet.net.http import UrlIterator
#from xnet.tools import ToolMixin_AddrIterator
#from xnet.debug import pdb


class UnsafePool(object):
    '''
        Naive non-threadsafe pool of items.
        Useful when working with greenlets as put() and get()
        doesn't block.
    '''
    def __init__(self, item_factory, size):
        self._size = size
        self._ready = [item_factory() for _ in xrange(size)]
        self._busy = []

    def put(self, item):
        index = self._busy.index(item)
        del self._busy[index]
        self._ready.append(item)

    def get(self):
        item = self._ready.pop()
        self._busy.append(item)
        return item

    def __iter__(self):
        return iter(self._ready)

    @property
    def ready(self):
        return len(self._busy) == 0



class BrowserPool(UnsafePool):
    pass


class SeleniumException(Exception):
    pass


class SeleniumTool(Tool):

    __toolname__ = 'webget'
    __itemname__ = 'url'
    __description__ = 'get information from web services'

    cmdline_options = [
        ('-b', '--browser', 'use this selenium webdriver browser',
            dict(dest='browser', metavar='firefox|chrome|ie|opera')),
        ('', '--proxy', 'use http/https proxy',
            dict(dest='proxy', metavar='host:port')),
        ('', '--keep', 'don\'t close browser windows at exit',
            dict(dest='keep', action='store_true')),
        ('-p', '--ports', 'use these ports for urls lacking port AND protocol components',
            dict(dest='ports', metavar='m-n,..')),
        ('-S', '--https', 'default to https when protocol is missing',
            dict(dest='https', action='store_true')),
        ('', '--xpath', 'grab elements matching xpath expression',
            dict(action='append', metavar='expr')),
        ('', '--xpath-delimiter', 'xpath output delimiter when using multiple --xpath\'s',
            dict(dest='xpath_delimiter', metavar='delim')),
        ('', '--xpath-strict', 'exit if not all --xpath\'s are matched',
            dict(dest='xpath_strict', action='store_true')),
        ('', '--tag-lines', 'prefix each line with current url',
            dict(dest='tag_lines', action='store_true')),
    ]

    @classmethod
    def print_source(cls):
        cls._print_source(__file__)

    _use_selenium = False

    @classmethod
    def __setup__(cls, options):
        from selenium import webdriver
        if not options.nr_microthreads:
            options.nr_microthreads = 1
        brname = (options.browser or 'firefox').lower()
        if options.proxy and brname != 'firefox':
            errmsg = '--proxy can only be used together with --browser=firefox'
            raise SeleniumException(errmsg)

        BrowserFactory = None
        if brname == 'firefox':
            BrowserFactory = webdriver.Firefox
            if options.proxy:
                from selenium.webdriver.common.proxy import (
                    Proxy,
                    ProxyType,
                )
                proxy = Proxy({
                    'proxyType': ProxyType.MANUAL,
                    'httpProxy': options.proxy,
                    'ftpProxy': options.proxy,
                    'sslProxy': options.proxy,
                    'noProxy': '',
                })
                BrowserFactory = lambda: webdriver.Firefox(proxy=proxy)
        elif brname == 'chrome':
            BrowserFactory = webdriver.Chrome
        elif brname in ('ie', 'explorer'):
            BrowserFactory = webdriver.Ie
        elif brname == 'opera':
            BrowserFactory = webdriver.Opera
        else:
            errmsg = 'Unknown selenium webdriver \'{0}\','
            errmsg += ' valid webdrivers are: firefox, chrome, ie, opera'
            raise SeleniumException(errmsg)
        #cls._BrowserFactory = BrowserFactory
        nr_microthreads = int(options.nr_microthreads or '1')
        cls._browser_pool = BrowserPool(BrowserFactory, nr_microthreads)

    @classmethod
    def __teardown__(cls, options):
        if not options.keep:
            browser_pool = cls._browser_pool
            if not browser_pool.ready:
                raise Warning('browser_pool not ready')
            for br in browser_pool:
                br.close()
            del cls._browser_pool

    def __init__(self, *args, **kw):
        super(SeleniumTool, self).__init__(*args, **kw)
        self._url = None

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

    def _get_host(self, url):
        return urlparse.urlparse(url).netloc

    def __action__(self, parse_result):
        result = {}
        browser = self._browser_pool.get()
        if browser is None:
            browser = self._BrowserFactory()
            self._browser = browser
        _start_url = self._start_url = parse_result['url']
        _response = None
        _body_unicode = None
        _body = ''
        _title = ''
        _xpath_result = ''
        #
        browser.get(_start_url)
        _body_unicode = browser.page_source
        _body = _body_unicode.encode('utf-8')
        _title = browser.title.encode('utf-8')

        if self.options.xpath:
            from xnet.net.http import HTMLParser
            htmlparser = HTMLParser(_body_unicode)
            #
            # If mutliple xpath expressions, separate results with newlines.
            #
            for xpath in self.options.xpath:
                if len(_xpath_result):
                    _xpath_result += '\n'
                _xpath_result += htmlparser.xpath(xpath,
                                                  match_delimiter=self.options.xpath_delimiter)

        #
        if hasattr(self.options, 'tag_lines') and self.options.tag_lines:
            tag = self._start_url + ':'
            _body = '\n' + tag + _body.replace('\n', '\n' + tag)

        result['start_url'] = _start_url
        result['start_host'] = self._get_host(_start_url)
        result['current_url'] = browser.current_url
        result['current_host'] = self._get_host(browser.current_url)
        result['response'] = _response
        result['body'] = _body
        result['body_unicode'] = _body_unicode
        result['title'] = _title
        result['xpath'] = _xpath_result
        self._browser_pool.put(browser)
        return result

    def __format__(self, line, parse_result, action_result):
        #start_url = action_result['url']
        #current_url = action_result['url']
        output = ''
        if self.options.xpath:
            output = action_result['xpath']
        else:
            output = action_result['body']
        return output

    @classmethod
    def __format_help__(cls):
        output = '''
Format variables for %s:

 host     - target host
 url      - target URL
 server   - Server header value
 body     - response body
 time     - time consumed by action, in ms
 pid      - PID of executing process
 grid     - Greenlet ID of executing process

Default format depend on commandline arguments.
        ''' % cls.__toolname__
        return output

    def __timeout__(self):
        return 'timeout {0}\n'.format(self._url)


def main():
    import xnet.tools.run
    xnet.tools.run.run(SeleniumTool)


if __name__ == "__main__":
    main()
    #doctest.testmod()
    #unittest.main()
