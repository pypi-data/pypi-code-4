#!/usr/bin/python
# coding: utf8

import urllib2
from lxml import etree
from os.path import expanduser
import os, errno

def getCacheDir():
    try:
        path = expanduser('~')+"/.cache/python/turnguard/com/wikiutils/"
        os.makedirs(path)
    except OSError as exc: # Python >2.5
        if exc.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else: raise
    return path

class NotInCacheError(Exception):
    pass

class WikiPage:
    def __init__(self,wikiurl, wikiXML):
        self.wikiurl = wikiurl
        self.error = wikiXML.find('.//error')
        if(self.error!=None):
            raise urllib2.HTTPError(None, 404, self.error.attrib["info"], None, None)           

        
        self.plainText = ""
        self.title = wikiXML.find('.//parse').attrib['displaytitle']
        self.links = [ l.text for l in wikiXML.iterfind(".//pl[@ns='0']") ]
        self.categories = [ c.text for c in wikiXML.iterfind(".//cl") ]
        self.externallinks = [ e.text for e in wikiXML.iterfind(".//el") ]       

        html = etree.fromstring(wikiXML.find('.//text').text, etree.HTMLParser())
        pt = etree.tostring(html,encoding='utf-8',method='text')
        self.plainText = ' '.join(pt.split())

    def getLinks(self):
        return self.links

    def getPlainText(self):
        return self.plainText

    def getExternalLinks(self):
        return self.externallinks

    def getCategories(self):
        return self.categories

    def getTitle(self):
        return self.title

    def getURL(self):
        return self.wikiurl
        

class WikiUtils(object):

    def __init__(self):        
        self.__defaultHeaders = { 'User-Agent' : 'Mozilla/5.0' }
        self.__mediaWikiAPI = 'http://en.wikipedia.org/w/api.php?action=parse&format=xml&page='
        self.__wikiBaseURL = 'http://en.wikipedia.org/wiki/'
        self.__cacheDir = getCacheDir()

    def __getFromCache(self, wikititle):
        try:
            with open(self.__cacheDir+wikititle, 'r') as f:
                return f.read()
        except IOError, e:
            raise NotInCacheError(e)

    def __writeToCache(self, wikititle, string):
        with open(self.__cacheDir+wikititle, 'a') as f:
            f.write(string)

    def getWikiPage(self, wikiurl=None, wikititle=None, cache=True):        

        if(wikiurl==None and wikititle==None):
            raise Exception("Either wikiurl or wikititle must be present")
        
        if(wikiurl!=None and wikititle==None):
            wikititle = wikiurl.split('wiki/')[1]

        if(wikiurl==None and wikititle!=None):
            wikiurl = self.__wikiBaseURL+wikititle
        
        if(cache==True):
            try:                
                return WikiPage(wikiurl, etree.fromstring(self.__getFromCache(wikititle)))
            except NotInCacheError:                
                req = urllib2.Request(self.__mediaWikiAPI+wikititle, None, self.__defaultHeaders)
                resp = urllib2.urlopen(req).read()
                self.__writeToCache(wikititle, resp)               
                return WikiPage(wikiurl, etree.fromstring(resp))
        else:
            req = urllib2.Request(self.__mediaWikiAPI+wikititle, None, self.__defaultHeaders)
            resp = urllib2.urlopen(req).read()
            self.__writeToCache(wikititle, resp)
            return WikiPage(wikiurl, etree.fromstring(resp))
