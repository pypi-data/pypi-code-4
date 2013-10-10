from Acquisition import aq_inner
from Products.CMFCore.utils import getToolByName
from Products.Five import BrowserView
from zope.component import getMultiAdapter
from plone.app.layout.viewlets.common import ViewletBase

import pkg_resources
try:
    pkg_resources.get_distribution('plone.app.collection')
except pkg_resources.DistributionNotFound:
    HAS_COLLECTIONS = False
else:
    HAS_COLLECTIONS = True
    from plone.app.collection.interfaces import ICollection

try:
    pkg_resources.get_distribution('plone.app.contenttypes>=1.0b2')
except pkg_resources.VersionConflict:
    # older versions don't have the dx-based-collections
    HAS_PAC = False
except pkg_resources.DistributionNotFound:
    HAS_PAC = False
else:
    HAS_PAC = True
    from plone.app.contentypes.interfaces import ICollection as IDXCollection


class DoormatView(BrowserView):
    """
    """

    def getDoormatTitle(self):
        """
        """
        title = ''
        if self.context.getShowTitle():
            title = self.context.Title()
        return title

    def getDoormatData(self):
        """ Return a dictionary like this:
        data = [
            {   'column_title: 'Column One',
                'column_sections: [
                {   'section_title': 'De Oosterpoort',
                    'section_links': [
                        {   'link_title': 'Some Title',
                            'link_url': 'http://some.whe.re',
                            'link_class': 'external-link',
                            'content': 'html content',
                            },
                        ]
                    },
                ]
            },
        ]
        """
        doormat = self.context
        data = []
        # Fetch Columns
        for column in doormat.listFolderContents():
            column_dict = {
                'column_title': column.Title(),
                'show_title': column.getShowTitle(),
                }
            column_sections = []
            sections = column.listFolderContents()

            # Fetch Categories from Column
            for section in sections:
                section_dict = {
                    'section_title': section.Title(),
                    'show_title': section.getShowTitle(),
                    }
                section_links = []
                objs = section.listFolderContents()

                # Loop over all link object in category
                for item in objs:
                    # Use the link item's title, not that of the linked content
                    title = item.Title()
                    text = ''
                    url = ''
                    link_class = ''

                    if item.portal_type == 'DoormatReference':
                        linked_item = item.getInternal_link()
                        if not linked_item:
                            continue
                        url = linked_item.absolute_url()
                    elif item.portal_type == "Link":
                        if item.meta_type.startswith('Dexterity'):
                            # A Dexterity-link
                            url = item.remoteUrl
                        else:
                            # Link is an Archetypes link
                            url = item.getRemoteUrl
                        link_class = "external-link"
                    elif item.portal_type == "Document":
                        if item.meta_type.startswith('Dexterity'):
                            # A Dexterity-link
                            text = item.text.output
                        else:
                            text = item.getText()
                    elif item.portal_type == "DoormatCollection":
                        if item.getCollection().portal_type == "Topic":
                            results = self.getCollection(item)

                            # Add links from collections
                            for nitem in results:
                                obj = nitem.getObject()

                                if (item.showTime):
                                    title = self.localizedTime(obj.modified())\
                                        + ' - ' + obj.title
                                else:
                                    title = obj.title

                                section_links.append({
                                    'content': '',
                                    'link_url': obj.absolute_url(),
                                    'link_title': title,
                                    'link_class': 'collection-item',
                                    })

                            # Add the read more link if it is specified
                            if item.getShowMoreLink():
                                section_links.append({
                                    'content': '',
                                    'link_url': item.getShowMoreLink(
                                        ).absolute_url(),
                                    'link_title': item.showMoreText,
                                    'link_class': 'read-more'
                                })

                            continue
                        elif item.getCollection().portal_type == "Collection":
                            results = self.getCollection(item)

                            # Add links from collections
                            for nitem in results:
                                obj = nitem.getObject()

                                if (item.showTime):
                                    title = self.localizedTime(obj.modified())\
                                        + ' - ' + obj.title
                                else:
                                    title = obj.title

                                section_links.append({
                                    'content': '',
                                    'link_url': obj.absolute_url(),
                                    'link_title': title,
                                    'link_class': 'collection-item',
                                    })

                            # Add the read more link if it is specified
                            if item.getShowMoreLink():
                                section_links.append({
                                    'content': '',
                                    'link_url': item.getShowMoreLink(
                                        ).absolute_url(),
                                    'link_title': item.showMoreText,
                                    'link_class': 'read-more'
                                })

                            continue
                        else:
                            url = ''
                            text = ("%s: This is not a collection, but a %s "
                                    ":-)" % (
                                        item.id,
                                        item.getCollection().portal_type))

                    if not (text or url):
                        continue

                    link_dict = {
                        'content': text,
                        'link_url': url,
                        'link_title': title,
                        'link_class': link_class,
                        }
                    section_links.append(link_dict)
                section_dict['section_links'] = section_links
                column_sections.append(section_dict)
            column_dict['column_sections'] = column_sections
            data.append(column_dict)
        return data

    def getCollection(self, item):
        col = item.getCollection()
        if item.limit > 0:
            if HAS_COLLECTIONS and ICollection.providedBy(col) or \
                    HAS_PAC and IDXCollection.providedBy(col):
                results = col.queryCatalog(b_size=item.limit)
            else:
                results = col.queryCatalog(sort_limit=item.limit)[:item.limit]
        else:
            results = col.getCollection().queryCatalog()

        return results

    def localizedTime(self, time):
        return getMultiAdapter(
            (self.context, self.request), name="plone").toLocalizedTime(time)


class DoormatViewlet(ViewletBase):

    def available(self):
        return self.doormat is not None

    @property
    def doormat(self):
        context = aq_inner(self.context)
        cat = getToolByName(context, 'portal_catalog')
        portal_state = getMultiAdapter((self.context, self.request),
                                       name=u'plone_portal_state')
        navigation_root_path = portal_state.navigation_root_path()
        # First try to find a doormat within the navigation root.
        doormats = cat(portal_type='Doormat', path=navigation_root_path,
                       sort_on='created')
        if doormats:
            return doormats[0].getObject()
        # #Optionally we could then try to find a doormat anywhere.
        # doormats = cat(portal_type='Doormat', sort_on='created')
        # if doormats:
        #    return doormats[0].getObject()
