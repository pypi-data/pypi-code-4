import zope.interface

class IConsolidatedHTMLDocument(zope.interface.Interface):
    """ Marker interface for consolidated HTML documents """ 

class IExportProvider(zope.interface.Interface):
    """ EXPERIMENTAL API """

    def getExportLink(context):
        """ Returns a link to be used for exporting the current conversions folder """

class IPublishingProvider(zope.interface.Interface):
    """ EXPERIMENTAL API """

    def getPublishLink(context):
        """ Returns a link to be used for publishing the current conversions folder """



