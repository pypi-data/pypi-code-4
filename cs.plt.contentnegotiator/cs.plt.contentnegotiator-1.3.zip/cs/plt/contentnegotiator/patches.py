__doc__ = """

This module patches PloneLanguageTool's getContentLanguage method
to work in a virtual hosting environment such as Plone served by Zope.
The original code uses the variable PATH_TRANSLATED from the request
but that variable has all the VirtualHostBase and domain keywords
used when virtualhosting your Plone site, so this small patch looks
at the request and if the application is run in a virtual hosted
environment, looks at VIRTUAL_URL_PARTS variable and if not at
PATH_TRANSLATED as usual.

This error has been reported to plone-users but has no fix yet.

"""

from ZODB.POSException import ConflictError

def getPatchedContentLanguage(self):
    """Checks the language of the current content if not folderish."""
    if not hasattr(self, 'REQUEST'):
        return []
    try: # This will actually work nicely with browserdefault as we get attribute error...
        #contentpath = self.REQUEST.get('PATH_TRANSLATED')
        contentpath = None
        if self.REQUEST.get('VIRTUAL_URL', None) is not None:
            contentpath = self.REQUEST.get('VIRTUAL_URL_PARTS')[1]
        else:
            contentpath = self.REQUEST.get('PATH_TRANSLATED')

        if contentpath is not None and contentpath.find('portal_factory') == -1:
            obj = self.unrestrictedTraverse(contentpath, None)
            if obj is not None:
                if obj.Language() in self.getSupportedLanguages():
                    return obj.Language()
    except ConflictError:
        raise
    except:
        pass
    return None


from logging import getLogger
log = getLogger('cs.plt.contentnegotiator')
log.info('Patching...')

from Products.PloneLanguageTool.LanguageTool import LanguageTool
LanguageTool._oldgetContentLanguage = LanguageTool.getContentLanguage
LanguageTool.getContentLanguage = getPatchedContentLanguage

log.info('Patching... done')
