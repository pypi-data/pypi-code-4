# -*- coding: utf-8 -*-
import argparse
import sys
from ConfigParser import RawConfigParser, NoOptionError, NoSectionError
from urllib2 import urlopen

VERSION_URL_TEMPLATE = "http://dist.plone.org/release/%s/versions.cfg"

parser = argparse.ArgumentParser(description='Plone version pinning')


def merge_versions(v1, v2):
    ''' Merge the versions from v1 with the ones from v2
    '''
    v1 = dict(v1)
    v2 = dict(v2)
    v2.update(v1)
    return [(x, y) for x, y in v2.iteritems()]


def sort_versions(v):
    ''' Return the versions sorted
    '''
    v.sort(key=lambda x: x[0])
    return v


class CFGParser(RawConfigParser):

    ''' Parse a URL
    '''
    _url = ''
    _version = ''

    optionxform = str

    def __init__(self, url):
        ''' Initialize our object

        :param version: a string like 4.3.1
        '''
        RawConfigParser.__init__(self)
        self._url = url
        self.urlfp = urlopen(self._url)
        self.readfp(self.urlfp)

    def get_extends_urls(self):
        ''' Get the extends from the buildout
        '''
        try:
            option = self.get('buildout', 'extends').strip()
        except (NoOptionError, NoSectionError):
            return []
        urls = [line.strip() for line in option.splitlines()]
        urls.reverse()
        return urls

    def get_versions(self):
        ''' Get's the versions from this file
        '''
        return self.items('versions')

    def get_merged_versions(self):
        ''' Get's the versions merged according to the extends
        '''
        urls = self.get_extends_urls()
        composed = [(self._url, self.get_versions())]
        for url in urls:
            cfg = CFGParser(url)
            composed.extend(cfg.get_merged_versions())
        return composed

    def __call__(self):
        ''' Calling This will output versions to the stdout
        '''
        merged_versions = self.get_merged_versions()
        merged_versions.reverse()
        for url, versions in merged_versions:
            print "## %s" % url
            for key, value in versions:
                print "%s = %s" % (key, value)
            print


class PloneCFGParser(CFGParser):

    ''' Parse a URL from dist.plone.org
    '''
    _version = ''

    def __init__(self, version):
        ''' Initialize our object

        :param version: a string like 4.3.1
        '''
        self._version = version
        CFGParser.__init__(self, VERSION_URL_TEMPLATE % version)


def main(return_tagdir=False):
    """ This will try to fetch versions from dist.plone.org
    """
    return PloneCFGParser(sys.argv[1])()
