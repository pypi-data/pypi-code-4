from zope.interface import implements
from zope.component import adapts

from plone.app.layout.nextprevious.interfaces import INextPreviousProvider
from plone.memoize.instance import memoize

from Products.CMFCore.utils import getToolByName

from collective.blogging.interfaces import IBlogMarker, IEntryMarker

class BlogNextPrevious(object):
    """Let a blog act as a next/previous provider. This will be 
    automatically found by the @@plone_nextprevious_view and viewlet.
    """

    implements(INextPreviousProvider)
    adapts(IBlogMarker)

    def __init__(self, context):
        self.context  = context
        
        sp = getToolByName(self.context, 'portal_properties').site_properties
        self.view_action_types = sp.getProperty('typesUseViewActionInListings', ())

    def getNextItem(self, obj):
        relatives = self.itemRelatives(obj.getId())
        return relatives["next"]
        
    def getPreviousItem(self, obj):
        relatives = self.itemRelatives(obj.getId())
        return relatives["previous"]

    @property
    def enabled(self):
        try:
            return self.context.getNextPreviousEnabled()
        except AttributeError:
            # Always enabled for Large Folders
            return True

    def getPosition(self, oid, contents):
        index = 0
        for b in contents:
            if b.getId == oid:
                return index
            index += 1
        return index

    @memoize
    def itemRelatives(self, oid):
        """Get the relative next and previous items
        """
        catalog  = getToolByName(self.context, 'portal_catalog')
        contents = [b for b in catalog(self.buildNextPreviousQuery())]
        position = self.getPosition(oid, contents)

        previous = None
        next     = None

        # Get the previous item
        if position - 1 >= 0:
            previous = self.buildNextPreviousItem(contents[position - 1])

        # Get the next item
        if position + 1 < len(contents):
            next = self.buildNextPreviousItem(contents[position + 1])

        nextPrevious = {
            'next'      : next,
            'previous'  : previous,
            }

        return nextPrevious
        
    def buildNextPreviousQuery(self):
        query                    = {'object_provides': IEntryMarker.__identifier__}
        query['sort_on']         = 'effective'
        query['sort_order']      = 'reverse'
        query['path']            = dict(query = '/'.join(self.context.getPhysicalPath()),
                                        depth = 1)
        # Filters on content
        query['is_default_page'] = False
        query['is_folderish']    = False
        return query

    def buildNextPreviousItem(self, brain):
        return {'id'          : brain.getId,
                'url'         : self.getViewUrl(brain),
                'title'       : brain.Title,
                'description' : brain.Description,
                'portal_type' : brain.portal_type,
                }

    def getViewUrl(self, brain):
        """create link and support contents that requires /view 
        """
        item_url = brain.getURL()
    
        #if brain.portal_type in self.view_action_types:
        #    item_url += '/view'
    
        return item_url