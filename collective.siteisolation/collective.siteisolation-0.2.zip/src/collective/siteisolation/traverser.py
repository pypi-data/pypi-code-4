# -*- coding: utf-8 -*-
from zope.component import adapts
from zope.interface import alsoProvides, Interface, implements
try:
    from zope.component.hooks import getSite
    getSite  # Pyflakes Fix
except ImportError:  # Plone < 4.3
    from zope.app.component.hooks import getSite
from zope.publisher.interfaces.http import IHTTPRequest
from zope.publisher.interfaces import IPublishTraverse
from ZPublisher.BaseRequest import DefaultPublishTraverse
from plone.memoize.forever import memoize
from collective.siteisolation.interfaces import (IIsolatedObject,
                                                 IPotentialBadRequest,
                                                 IObjectToIsolate)


@memoize
def getRootIsolatedObjects():
    """
    Return the objects on the Zope root (we are assuming here that your sites
    are on the top level) that have to be isolated from each others
    """
    return frozenset([id for id, obj in getSite().aq_parent.objectItems() if IObjectToIsolate.providedBy(obj)])


class BaseIsolatedTraverser(DefaultPublishTraverse):
    """
    Traverser base class
    """

    def _traverseAndCheckObject(self, request, name):
        """
        This method fetch the object using the default traverser.
        If traversed name match one of the isolated object then raise a
        KeyError to return a 404 to the user. Otherwise it just return the
        object returned by the default traverser.
        """
        obj = super(BaseIsolatedTraverser, self).publishTraverse(request, name)
        if name in getRootIsolatedObjects():
            if IObjectToIsolate.providedBy(obj):
                raise KeyError(name)
        return obj


class IsolatedSiteTraverser(BaseIsolatedTraverser):
    """
    This traverser is applied only once you traverse an IIsolatedObject.

    This traverser look first if one of the names to be traversed matches
    with one of the root isolated objects. Then

        * if None of them match then it use the default traverser (see DefaultPublishTraverse) ;

        * if one of them match, we mark the request as being a potentially bad
          request and check if the first name we are traversing is one of the
          isolated objects.
    """
    adapts(IIsolatedObject, IHTTPRequest)
    implements(IPublishTraverse)

    def publishTraverse(self, request, name):
        namesToTraverse = frozenset([name] + self.request['TraversalRequestNameStack'])
        knownRootObjects = getRootIsolatedObjects()
        if namesToTraverse.intersection(knownRootObjects):
            alsoProvides(self.request, IPotentialBadRequest)
            return self._traverseAndCheckObject(request, name)
        else:
            return super(IsolatedSiteTraverser, self).publishTraverse(request, name)


class IsolatedRequestTraverser(BaseIsolatedTraverser):
    """
    This traverser is applied only for marked request with IPotentialBadRequest
    interface.

    It just check if the name we are traversing is one of the
    isolated objects.
    """
    adapts(Interface, IPotentialBadRequest)
    implements(IPublishTraverse)

    def publishTraverse(self, request, name):
        return self._traverseAndCheckObject(request, name)
