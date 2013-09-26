"""Definition of the XMLTransformer content type
"""

from zope.interface import implements

from Products.Archetypes import atapi
from Products.ATContentTypes.content import base
from Products.ATContentTypes.content import schemata

# -*- Message Factory Imported Here -*-
from drchitu.XMLTransformer import XMLTransformerMessageFactory as _

from drchitu.XMLTransformer.interfaces import IXMLTransformerType
from drchitu.XMLTransformer.config import PROJECTNAME

# from DateTime import DateTime
import urllib
from lxml import etree
import libxml2
import libxslt
from Products.PythonScripts.standard import url_quote
import string

# for a unix timestamp
from datetime import datetime
import time

# for search/portal_transforms
from Products.CMFCore.utils import getToolByName

# debugging
from pprint import pprint

# logging
import logging
from Products.statusmessages.interfaces import IStatusMessage

XMLTransformerTypeSchema = schemata.ATContentTypeSchema.copy() + atapi.Schema((

    # -*- Your Archetypes field definitions here ... -*-

    # override id definition

    # XML
    atapi.BooleanField(
        'useXmlUrl',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u"Use XML from URL?"),
            description=_(u"Check this if you want to fetch the XML from the URL given in the XML URL field."),
        ),
    ),

    atapi.StringField(
        'xmlUrl',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"XML Url"),
            description=_(u"Enter the URL where to fetch the XML from"),
        ),
        required=False,
    ),

    atapi.FileField(
        'xmlFile',
        storage=atapi.AnnotationStorage(),
        widget=atapi.FileWidget(
            label=_(u"XML File Upload"),
            description=_(u"Upload the XML source here."),
        ),
    ),

    atapi.LinesField(
        'xmlParameters',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"XML Parameters"),
            description=_(u"Enter key-value pairs separated by an equal sign, one line per pair. For example: foo=bar."),
        ),
    ),
    
    # XLST fields
    atapi.BooleanField(
        'useXsltUrl',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u"Use XSLT from Url?"),
            description=_(u"Check this if you want to fetch the XSLT from the URL given in the XSLT URL field."),
        ),
    ),


    atapi.StringField(
        'xsltUrl',
        storage=atapi.AnnotationStorage(),
        widget=atapi.StringWidget(
            label=_(u"XSLT Url"),
            description=_(u"Enter the URL of the XSLT that will be used for processing."),
        ),
        required=False,
    ),

    atapi.FileField(
        'xsltFile',
        storage=atapi.AnnotationStorage(),
        widget=atapi.FileWidget(
            label=_(u"XSLT File"),
            description=_(u"Upload the XSLT source here."),
        ),
    ),

    atapi.LinesField(
        'xsltParameters',
        storage=atapi.AnnotationStorage(),
        widget=atapi.LinesWidget(
            label=_(u"XSLT Parameters"),
            description=_(u"Enter key-value pairs separated by an equal sign, one line per pair. For example: 'foo=bar' (without the quotes). To pass GET parameters from the URL use the following syntax: 'foo=GET_bar', to pass the GET parameter bar to the value foo. You can also use python expressions here by using a 'python:' prefix as in 'year=python:__import__('datetime').datetime.now().year'"),
        ),
    ),

    # Result
    atapi.TextField(
        'transformationResult',
        default_content_type = 'text/html',
        default_output_type = 'text/html',
        allowable_content_types=('text/plain', 'text/html',),
        storage=atapi.AttributeStorage(),
        searchable=True,
        widget=atapi.TextAreaWidget(
            label=_(u"Transformation Result"),
            description=_(u"Result of the XML/XSLT Transformation process. Automatically filled."),
        ),
    ),

    # store the transformation result for searching in transformationResult?
    atapi.BooleanField(
        'cacheTransformationResult',
        storage=atapi.AnnotationStorage(),
        widget=atapi.BooleanWidget(
            label=_(u"Cache Transformation Result"),
            description=_(u"Cache the Transformation Result to enable searching for it through Plones search interface?"),
        ),
        default=_(u"True"),
    ),

    # stores how long the result should be stored/cached
    atapi.IntegerField(
        'cacheTime',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Cache time (seconds)"),
            description=_(u"Enter the cache time in seconds until the stored transformation result gets invalid. Default 0 = don't cache. 86400 = 24h (1 day)"),
        ),
        required=True,
        default=_(u"0"),
        validators=('isInt'),
    ),

    atapi.IntegerField(
        'lastCached',
        storage=atapi.AnnotationStorage(),
        widget=atapi.IntegerWidget(
            label=_(u"Last cached"),
            description=_(u"The time the cache was last written as a unix timestamp"),
        ),
        default=_(u"0"),
        validators=('isInt'),
    ),

    # Rich Text fields for pre and post content
    atapi.TextField(
        'contentPre',
        default_content_type = 'text/html',
        default_output_type = 'text/html',
        allowable_content_types=('text/plain', 'text/html',),
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Pre content"),
            description=_(u"Enter text/html content that should be displayed before the XMLTransformer result"),
        ),
    ),
    atapi.TextField(
        'contentPost',
        default_content_type = 'text/html',
        default_output_type = 'text/html',
        allowable_content_types=('text/plain', 'text/html',),   
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Post content"),
            description=_(u"Enter text/html content that should be displayed after the XMLTransformer content"),
        ),
    ),

    # Rich Text for error message
    atapi.TextField(
        'contentError',
        default_content_type = 'text/html',
        default_output_type = 'text/html',
        allowable_content_types=('text/plain', 'text/html',),
        storage=atapi.AnnotationStorage(),
        widget=atapi.RichWidget(
            label=_(u"Error Content"),
            description=_(u"Enter text here that will be displayed in case an error occurs during the transformation"),
        ),
    ),




    # We need: 
    # *) XML source url
    # *) XML url parameters
    # *) XSLT source url
    # *) XSLT Parameters
    # *) Id, Title, Url, Description
    # *) Blob Field for transformation result
    # *) Cache expiry string


))

# make the transformationresult invisible on editing it
XMLTransformerTypeSchema["transformationResult"].widget.visible = {"edit": "invisible" }
XMLTransformerTypeSchema["lastCached"].widget.visible = {"edit": "invisible", "view": "invisible"  }
XMLTransformerTypeSchema["useXmlUrl"].widget.visible = {"view": "invisible" }
XMLTransformerTypeSchema["xmlUrl"].widget.visible = {"view": "invisible" }
XMLTransformerTypeSchema["xmlFile"].widget.visible = {"view": "invisible" }
XMLTransformerTypeSchema["xmlParameters"].widget.visible = {"view": "invisible" }
XMLTransformerTypeSchema["useXsltUrl"].widget.visible = {"view": "invisible" }
XMLTransformerTypeSchema["xsltUrl"].widget.visible = {"view": "invisible" }
XMLTransformerTypeSchema["xsltFile"].widget.visible = {"view": "invisible" }
XMLTransformerTypeSchema["xsltParameters"].widget.visible = {"view": "invisible" }
XMLTransformerTypeSchema["title"].widget.visible = {"view": "visible"}


schemata.finalizeATCTSchema(XMLTransformerTypeSchema, moveDiscussion=False)


class XMLTransformerType(base.ATCTContent):
    """XMLTransformer Content Type"""
    implements(IXMLTransformerType)

    meta_type = "XMLTransformerType"
    schema = XMLTransformerTypeSchema

    # internal variable to store whether get parameters are used or not
    isUsingGetParameters = False
    isError = False
    errorMessage = ""
    xmlQueryString = None
    xsltParamDict = None

    # logging
    logger = logging.getLogger("Plone")

    # test method, deprecated
    def someMethod(self):
        # see http://developer.plone.org/misc/datetime.html
        # zope_DT = DateTime() # this is now.
        # python_dt = zope_DT.asdatetime()
        # zope_DT = DateTime(python_dt)
        # zope_DT = DateTime()
        # python_dt = zope_DT.asdatetime()
        # self.transformationResult = "Foobar: " + str(python_dt)
      return "somestring"

    # test method, deprecated
    def testGetXML(self):
        return self.getXmlUrl

    def handleError(self, message, exception = None):
        # log exception
        if (exception != None):
            self.logger.exception(exception)

        # TODO if admin
        # Open Plone status messages interface for this request
        messages = IStatusMessage(self.REQUEST)
        messages.addStatusMessage(message,type=u"error")

        self.isError = True
        self.errorMessage = message

        return self.errorMessage

    # return the content type last modified as unix timestamp
    def _getLastModified(self):
        return int(self.modified())

    # get current unix timestamp
    def _getUnixTimestamp(self):
        return time.time()

    # read and return the xml form theurl specified in the field xmlUrl
    def _fetchXmlUrl(self):
        url = self.getXmlUrl()
        if ('?' in url):
            url = url + '&' + self._getXmlQueryString()
        else:
            url = url + '?' + self._getXmlQueryString()
        # get url content
        f = urllib.urlopen(url)
        result = f.read()
        f.close()
        return result

    # read and return the xslt from the url specified in the field xsltUrl
    def _fetchXsltUrl(self):
        f = urllib.urlopen(self.getXsltUrl())
        result = f.read()
        f.close()
        return result

    def _fetchXmlFile(self):
        try:
            return str(self.getXmlFile())
        except AttributeError,e:
            print self.handleError("ERROR: AttributeError while fetching XML file",e)
            return ""


    def _fetchXsltFile(self):
        try:
            return str(self.getXsltFile())
        except AttributeError,e:
            print self.handleError("ERROR: AttributeError while fetching Xslt file",e)
            return ""


    def _getArrayFromKeyValueItem(self, item):
        tmp = string.split(item, "=")
        tmpVarname = tmp[0]
        tmpVarvalue = tmp[1]
        if (tmpVarvalue.startswith("GET_")):
            getKey = tmpVarvalue[4:]
            # pprint(dir(self.REQUEST.form.get("foo")))
            try:
                if (self.REQUEST.form[getKey] != ""):
                    # print "Request object foo found: " + self.REQUEST.form["foo"]
                    # set the stylesheet parameter
                    # paramDict[tmpVarname] = self.REQUEST.form[getKey]
                    tmpVarvalue = self.REQUEST.form[getKey]
                    self.isUsingGetParameters = True
                    # print "Using get value, caching will be disabled"
                else:
                    # print "Request object foo empty"
                    tmpVarvalue = ""
            except KeyError:
               # print "Request parameter " + getKey + " not found but expected"
               tmpVarvalue = ""
        elif (tmpVarvalue.startswith("python:")):
            pythonExpr = tmpVarvalue[7:]
            try:
                tmpVarvalue = eval(pythonExpr)
            except Error,e:
                print self.handleError("ERROR: Could not evaluate python expression",e)
                tmpVarvalue = ""
        return [tmpVarname, tmpVarvalue]


    def _makeQueryStringFromField(self, paramTuples):
        queryString = ""
        i = 0
        for item in paramTuples:
            if (item.startswith("#")):
                continue
            tmp = self._getArrayFromKeyValueItem(item)
            if (tmp[1] != ""):
                queryString = queryString+url_quote(tmp[0]) + '=' + url_quote(tmp[1])
                # if its not the last, add an &
                if (i < (len(paramTuples)-1)):
                    queryString=queryString + '&'
            i += 1
        return queryString

    # needed to fetch the XML query String
    def _getXmlQueryString(self, override = False):
        if (self.xmlQueryString is None or override == True):
            self.xmlQueryString = self._makeQueryStringFromField(self.getXmlParameters())
        return self.xmlQueryString

    # internal method, deprecated
    def _getXsltQueryString(self):
        return self._makeQueryStringFromField(self.getXsltParameters())

    def _getParamDict(self, parameters):
        # pass in parameters     
        paramDict = {}
        for item in parameters:
             if (item.startswith("#")):
                 continue
             tmp = self._getArrayFromKeyValueItem(item)
             if (tmp[1] != ""):
                paramDict[tmp[0]] = '"' + tmp[1] + '"'
        return paramDict

    # transform the given xml and xslt string using lxml
    def _transform(self, xmlstr, xsltstr):
        result = ""
        if (xmlstr is None or xmlstr == "" or xsltstr is None or xsltstr == ""):
            print self.handleError("Error, no XML or XSLT given")
            return result
        try:
            # using lxml
            # load xml file 
            xml_root = etree.XML(xmlstr)
            # load xslt file 
            xslt_root = etree.XML(xsltstr)
            # load transformer 
            transform = etree.XSLT(xslt_root)
            # convert to string and return
            result = etree.tostring(transform(xml_root, **dict(self._getXsltParamDict())))
        except Exception,e:
            print self.handleError("An error occured during the transformation",e)
        return result

    # writes the cache field
    def _writeCache(self, value):
        timenow = self._getUnixTimestamp()
        self.setTransformationResult(value)
        self.setLastCached(timenow)
        
        # reindex search catalog
        # http://developer.plone.org/content/manipulating.html
        self.reindexObject(idxs=['transformationResult'])

        return True

    def _getXsltParamDict(self, override = False):
        if (self.xsltParamDict is None or override == True):
            self.xsltParamDict = self._getParamDict(self.getXsltParameters())
        return self.xsltParamDict

    # check if get parameters are goind to be processed
    def _isUsingGetParameters(self):
        return self.isUsingGetParameters

    # is caching allowed?
    def _isCachingAllowed(self):
        # if (self.getCacheTransformationResult()):
          #    print "Caching checkbox is: true"
        #else:
          #    print "Caching checkbox is: false" 
        #if (self._isUsingGetParameters()):
        #    print "IsUsingGetParameters is: true"
          #else:
          #    print "IsUsingGetParameters is: false"
        return (self.getCacheTransformationResult() == True and self._isUsingGetParameters() != True)

    # checks whether the cache is expired
    def _isCacheExpired(self):
        isCacheExpired = False
        timeNow = int(self._getUnixTimestamp())
        cacheTime = int(self.getCacheTime())
        lastCachedTime = int(self.getLastCached())
        if (lastCachedTime + cacheTime < timeNow):
            isCacheExpired = True
        # expire cache, if last modified is newer than last cache time
        if (self._getLastModified() >= lastCachedTime):
            isCacheExpired = True
        # return boolean
        return isCacheExpired

    def _isCacheControlHeaderSet(self):
        cacheControl = self.REQUEST.get_header("Cache-Control")
        if (cacheControl != None):
            if (cacheControl == "no-cache"):
                # print "Cache-Control header is set"
                return True
        return False

    def init(self):
        self.isUsingGetParameters = False
        self._getXmlQueryString(True)
        self._getXsltParamDict(True)
        self.isError = False
        self.errorMessage = ""

    def _getXmlStr(self):
        if (self.getUseXmlUrl() == True):
            # print "Using XML URL"
            return self._fetchXmlUrl()
        else:
            # print "Using XML File"
            return self._fetchXmlFile()

    def _getXsltStr(self):
        if (self.getUseXsltUrl() == True):
            # print "Using XSLT URL"
            return self._fetchXsltUrl()
        else:
            # print "Using XSLT File"
            return self._fetchXsltFile()


    def sendHTTPResponseHeaders(self):
        request = self.REQUEST
        response = request.response
        # add powered-by
        response.setHeader("X-Powered-By", "XMLTransformer, a plone product by Dr. Christoph Hermann IT-Unternehmensberatung, see http://drhermann.de/")
        # keep the connection alive (bc we mostly include many images in order to speed up latency)
        response.setHeader("Connection", "keep-alive")
        if (self._isCachingAllowed()):
            response.setHeader("Last-Modified", time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime(int(self.getLastCached()))))
            # Expires: add cachetime to last modified
            expiresTimestamp = (int(self.getCacheTime()) + int(self.getLastCached()))
            expires = time.strftime("%a, %d-%b-%Y %T GMT", time.gmtime(expiresTimestamp))
            response.setHeader("Expires", expires)
            # cache-control
            response.setHeader("Cache-Control","max-age=%s, must-revalidate" % str(self.getCacheTime()))
        else:
            response.setHeader("Pragma", "no-cache")

    # public method
    def transform(self):
        # get parameters
        # running this methods checks whether GET parameters are used or not
        self.init()
        
        result = ""
        # check caching
        if (self._isCachingAllowed()):
            if (self._isCacheExpired() or self._isCacheControlHeaderSet()):
                # print "Cache has expired or force clear, rewriting"
                # perform transformation 
                result = self._transform(self._getXmlStr(), self._getXsltStr())
                # write cache
                self._writeCache(result)
            # read from cache
            else:
                # print "Retrieving cached value"
                # read value from cache
                result = self.getTransformationResult()
        else:
            # print "Caching disabled"
            # ignore caching, pass transformation result directly
            result = self._transform(self._getXmlStr(), self._getXsltStr()) 
        # run transformation
       
        # send caching (or not) HTTP headers
        self.sendHTTPResponseHeaders()
 
        # return result
        return result


    def SearchableText(self):
        """
        Override searchable text logic based on the requirements.

        This method constructs a text blob which contains all full-text
        searchable text for this content item.

        This method is called by portal_catalog to populate its SearchableText index.
        """

        # Speed up string concatenation ops by using a buffer
        entries = []

        # plain text fields we index from ourself,
        # a list of accessor methods of the class
        plain_text_fields = ("Title", "Description")

        # HTML fields we index from ourself
        # a list of accessor methods of the class
        html_fields = ("getContentPre", "getTransformationResult", "getContentPost")

        def read(accessor):
            """
            Call a class accessor method to give a value for certain Archetypes field.
            """
            try:
                value = accessor()
            except:
                value = ""

            if value is None:
                value = ""

            return value

        # Concatenate plain text fields as is
        for f in plain_text_fields:
            if (f != None):
                accessor = getattr(self, f)
                value = read(accessor)
                entries.append(value)

        transforms = getToolByName(self, 'portal_transforms')

        # Run HTML valued fields through text/plain conversion
        for f in html_fields:
            if (f != None):
                accessor = getattr(self, f)
                value = read(accessor)

                if value != "":
                    stream = transforms.convertTo('text/plain', value, mimetype='text/html')
                    value = stream.getData()

                entries.append(value)

        # Plone accessor methods assume utf-8
        def convertToUTF8(text):
            if type(text) == unicode:
                return text.encode("utf-8")
            return text

        entries = [ convertToUTF8(entry) for entry in entries ]

        # Concatenate all strings to one text blob
        return " ".join(entries)


atapi.registerType(XMLTransformerType, PROJECTNAME)
