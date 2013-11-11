from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from collective.base.interfaces import IAdapter
from plone.app.contentlisting.interfaces import IContentListing
from plone.memoize.instance import memoize
from zope.interface import implements


class Adapter(object):
    """Base class for adapters"""

    implements(IAdapter)

    def __init__(self, context):
        self.context = context

    @memoize
    def catalog(self):
        """Return portal_catalog"""
        return getToolByName(self.context, 'portal_catalog')

    @memoize
    def context_path(self):
        """Path of the context"""
        return '/'.join(aq_inner(self.context).getPhysicalPath())

    def get_brains(self, interfaces=None, **query):
        """In default, find from path under the context."""

        # Interfaces
        if interfaces is not None:
            if not isinstance(interfaces, list):
                interfaces = [interfaces]
            object_provides = query.get('object_provides') or []
            if not isinstance(object_provides, list):
                object_provides = [object_provides]
            query['object_provides'] = [interface.__identifier__ for interface in interfaces] + object_provides

        # Set default path
        path = query.get('path')
        if path is None:
            path = self.context_path()

        # Depth
        depth = query.get('depth')
        if depth is not None:
            path = {'query': path, 'depth': depth}
            del query['depth']
        query['path'] = path
        sort_limit = query.get('sort_limit')

        # Unrestricted
        unrestricted = query.get('unrestricted')
        catalog = self.catalog()
        if unrestricted:
            catalog = catalog.unrestrictedSearchResults

        brains = catalog(query)
        if sort_limit:
            return brains[:sort_limit]

        return brains

    def get_objects(self, interfaces=None, **query):
        """Get objects."""
        return [brain.getObject() for brain in self.get_brains(interfaces=interfaces, **query)]

    def get_brain(self, interfaces=None, **query):
        """Get brain which is supposed to be only one."""
        brains = self.get_brains(interfaces=interfaces, **query)
        if brains:
            return brains[0]

    def get_object(self, interfaces=None, **query):
        """Get object which is supposed to be only one."""
        brain = self.get_brain(interfaces=interfaces, **query)
        if brain:
            return brain.getObject()

    def get_content_listing(self, interfaces=None, **query):
        """Get ContentListing from brains gotten from get_brains method."""
        return IContentListing(self.get_brains(interfaces=interfaces, **query))

    def getSessionData(self, create=True):
        """Returns getSessionData method.

        :param create: True or False
        :type create: boolean

        :rtype: method
        """
        return getToolByName(self.context, 'session_data_manager').getSessionData(create=create)

    @memoize
    def event_datetime(self, item):
        """
        Returns datetime of event.

        1) When the start and end time are the same:
            Feb 25, 2013 12:00 AM

        2) When the start and end date are the same but not time:
            Feb 26, 2013 08:00 PM - 10:00 PM

        3) When the start and end date are different:
            Feb 27, 2013 12:00 AM - Feb 28, 2013 12:00 AM

        :param item: Instance
        :type item: plone.app.contentlisting.catalog.CatalogContentListingObject

        :rtype: unicode
        """
        start = item.start
        end = item.end
        toLocalizedTime = self.context.restrictedTraverse('@@plone').toLocalizedTime
        start_dt = toLocalizedTime(start, long_format=True)
        if start.Date() == end.Date():
            if start == end:
                dt = start_dt
            else:
                end_time = toLocalizedTime(end, time_only=True)
                dt = u'{} - {}'.format(start_dt, end_time)
        else:
            end_dt = toLocalizedTime(end, long_format=True)
            dt = u'{} - {}'.format(start_dt, end_dt)

        return dt

    @memoize
    def portal(self):
        """Returns portal object."""
        return getToolByName(self.context, 'portal_url').getPortalObject()

    @memoize
    def portal_path(self):
        """Returns portal path."""
        return '/'.join(self.portal().getPhysicalPath())

    @memoize
    def membership(self):
        return getToolByName(self.context, 'portal_membership')
