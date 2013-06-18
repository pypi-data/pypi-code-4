import logging

from AccessControl import Unauthorized
from Acquisition import aq_inner
try:
    try:
        from Products.Archetypes.UIDCatalog import UIDCatalogBrains
    except ImportError:
        from Products.Archetypes.ReferenceEngine import UIDCatalogBrains
    try:
        from Products.Archetypes.UIDCatalog import UIDResolver
    except ImportError:
        from Products.Archetypes.ReferenceEngine import ReferenceResolver as UIDResolver
    from Products.CMFCore.utils import getToolByName
    try:
        from Products.Archetypes.UIDCatalog import logger
    except ImportError:
        logger = logging.getLogger('Archetypes')
    PATCH_AT = True
except ImportError:
    PATCH_AT = False
from Products.ZCatalog.ZCatalog import ZCatalog
from zExceptions import NotFound
try:
    from ZODB.POSException import ConflictError
except ImportError:
    class ConflictError(Exception):
        pass


if PATCH_AT:
    # There doesn't seem to be a clear reason why this was even overridden in
    # the first place.
    del UIDResolver.resolve_url

    def getObject(self, REQUEST=None):
        """
        Used to resolve UIDs into real objects. This also must be
        annotation aware. The protocol is:
        We have the path to an object. We get this object. If its
        UID is not the UID in the brains then we need to pull it
        from the reference annotation and return that object

        Thus annotation objects store the path to the source object
        """
        obj = None
        try:
            path = self.getPath()
            if isinstance(path, basestring):
                path = path.split('/')
            try:
                parent = getToolByName(self, 'portal_url').getPortalObject()
                if len(path) > 1:
                    parent = parent.unrestrictedTraverse(path[:-1])

                obj = parent.restrictedTraverse(path[-1])
                obj = aq_inner(obj)
            except (Unauthorized, ConflictError, KeyboardInterrupt):
                raise
            except (KeyError, AttributeError, NotFound):
                pass

            if obj is None:
                if REQUEST is None:
                    REQUEST = self.REQUEST
                obj = self.aq_parent.resolve_url(self.getPath(), REQUEST)

            return obj
        except (Unauthorized, ConflictError, KeyboardInterrupt):
            raise
        except:
            logger.log(logging.INFO,
                'UIDCatalogBrains getObject raised an error', exc_info=True)

    UIDCatalogBrains.getObject = getObject


ZCatalog.resolve_path__roles__ = ()
ZCatalog.resolve_url__roles__ = ()
