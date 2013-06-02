from Acquisition import aq_inner
from zope.interface import implements, implementer, Interface
#import zope.component
from zope.component import getUtilitiesFor, adapter

import Products.Archetypes.interfaces
from p4a.subtyper import interfaces


class _DescriptorsMixin(object):

    def __init__(self, possible=[], comment=None):
        self._possible = possible
        self._comment = comment

    @property
    def possible(self):
        return self._possible

    def __str__(self):
        return '<PossibleDescriptors comment=%s>' % (self._comment or '')
    __repr__ = __str__


class PossibleDescriptors(_DescriptorsMixin):
    implements(interfaces.IPossibleDescriptors)


class PortalTypedPossibleDescriptors(_DescriptorsMixin):
    implements(interfaces.IPortalTypedPossibleDescriptors)


@adapter(Products.Archetypes.interfaces.IBaseFolder)
@implementer(interfaces.IPossibleDescriptors)
def folderish_possible_descriptors(context):
    possible = getUtilitiesFor(\
               interfaces.IFolderishContentTypeDescriptor)
    possible = [(n, c) for n, c in possible]
    return PossibleDescriptors(possible, 'folderish')


@adapter(Interface)
@implementer(interfaces.IPossibleDescriptors)
def nonfolderish_possible_descriptors(context):
    portal_type = getattr(aq_inner(context), 'portal_type', None)
    if portal_type is None:
        return PossibleDescriptors()

    all = getUtilitiesFor(\
          interfaces.IContentTypeDescriptor)
    all = set([(n, c) for n, c in all])
    folderish = getUtilitiesFor(\
          interfaces.IFolderishContentTypeDescriptor)
    folderish = set([(n, c) for n, c in folderish])

    return PossibleDescriptors(list(all.difference(folderish)),
                               'nonfolderish')


@adapter(Products.Archetypes.interfaces.IBaseFolder)
@implementer(interfaces.IPortalTypedPossibleDescriptors)
def portal_typed_folderish_possible_descriptors(context):
    portal_type = getattr(aq_inner(context), 'portal_type', None)
    if portal_type is None:
        return PortalTypedPossibleDescriptors()

    possible = getUtilitiesFor(\
               interfaces.IPortalTypedFolderishDescriptor)
    return PortalTypedPossibleDescriptors([(n, c) for n, c in possible
                                           if c.for_portal_type == portal_type],
                                           'portal_typed_folderish')


@adapter(Interface)
@implementer(interfaces.IPortalTypedPossibleDescriptors)
def portal_typed_nonfolderish_possible_descriptors(context):
    portal_type = getattr(aq_inner(context), 'portal_type', None)
    if portal_type is None:
        return PortalTypedPossibleDescriptors()

    all = getUtilitiesFor(\
          interfaces.IPortalTypedDescriptor)
    folderish = getUtilitiesFor(\
          interfaces.IPortalTypedFolderishDescriptor)

    all = set([(n, c) for n, c in all if c.for_portal_type == portal_type])
    folderish = set([(n, c) for n, c in folderish
                     if c.for_portal_type == portal_type])

    return PortalTypedPossibleDescriptors(list(all.difference(folderish)),
                               'portal_typed_nonfolderish')
