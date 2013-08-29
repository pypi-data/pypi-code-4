from string import Template
from Acquisition import aq_inner
from zope.component import getMultiAdapter
from AccessControl import Unauthorized
from Products.CMFPlone.utils import base_hasattr
 
from zope.interface import implements

from Products.ATContentTypes.interface import (IATTopic, IATFolder, IATBTreeFolder,
                                                IATNewsItem, IATEvent, IATLink, IATImage,
                                                IATFile)
try:
    from Products.CMFPlone import Batch
except ImportError:
    # plone 4.1
    from Products.CMFPlone.PloneBatch import Batch
from Products.Five import BrowserView

from plone.memoize import view

from collective.blogging.interfaces import IEntryMarker, IBloggingView
from collective.blogging import SHARING_PROVIDERS

class BlogView(BrowserView):
    """ A blog browser view """

    implements(IBloggingView)

    def computeRelatedItems(self, context=None):
        if not context:
            context = self.context
        if base_hasattr(context, 'getRelatedItems'):
            outgoing = context.getRelatedItems()
            incoming = []
            # if you want to show up the items which point to this one, too, then use
            # the line below
            #incoming = context.getBRefs('relatesTo')
            res = []
            mtool = context.portal_membership

            in_out = outgoing + incoming
            for d in range(len(in_out)):
                try:
                    obj = in_out[d]
                except Unauthorized:
                    continue
                if obj not in res:
                    if mtool.checkPermission('View', obj):
                        res.append(obj)
            return res
    
    def __init__(self, context, request):
        super(BlogView, self).__init__(context, request)
        self.context = context
        self.request = request

    @property
    def tools(self):
        return getMultiAdapter((self.context, self.request), name=u'plone_tools')

    @property
    def portal_state(self):
        return getMultiAdapter((self.context, self.request), name=u'plone_portal_state')

    def getFieldValue(self, name, obj=None):
        if obj is None:
            obj = self.context

        field = obj.getField(name)
        if field:
            return field.get(obj)
        return None

    @view.memoize
    def contents(self):
        brains = []
        criteria = {}

        # filter criteria
        subject = self.request.get('Subject', None)
        if subject and subject != ['']:
            criteria['Subject'] = subject

        year = self.request.get('publish_year', None)
        if year:
            criteria['publish_year'] = int(year)

        month = self.request.get('publish_month', None)
        if month:
            # Note: months are indexed as for example '03'
            criteria['publish_month'] = month

        if self.is_topic:
            brains = self.context.queryCatalog(criteria)
        else:
            criteria['object_provides'] = IEntryMarker.__identifier__
            criteria['path'] = '/'.join(self.context.getPhysicalPath())
            criteria['sort_on'] = 'effective'
            criteria['sort_order'] = 'reverse'
            brains = self.tools.catalog()(criteria)
        return brains

    def batch(self):
        b_start = self.request.get('b_start', 0)
        return Batch(self.contents(), self.batch_size, int(b_start), orphan=0)

    @property
    def count(self):
        return len(self.contents())

    @property
    def is_folder(self):
        return IATFolder.providedBy(self.context) or \
            IATBTreeFolder.providedBy(self.context)

    @property
    def is_topic(self):
        return IATTopic.providedBy(self.context)

    @property
    def site_props(self):
        pprops = self.tools.properties()
        return getattr(pprops, 'site_properties')

    @property
    def getText(self):
        text_field = self.context.getField('text')
        if text_field:
            return text_field.get(self.context)
        return self.context.getField('blog_text').get(self.context)

    @property
    def show_about(self):
        return not self.portal_state.anonymous() or \
            self.site_props.getProperty('allowAnonymousViewAbout', False)

    @property
    def show_body(self):
        field = self.context.getField('enable_full')
        if field:
            return field.get(self.context)
        return False

    @property
    def batch_size(self):
        field = self.context.getField('batch_size')
        if field:
            return field.get(self.context)
        return 10

    # Image related
    def is_image(self, obj):
        return IATImage.providedBy(obj)

    def image_size(self, obj):
        context = aq_inner(obj)
        return context.getObjSize(context)

    # News Item related
    def is_newsitem(self, obj):
        return IATNewsItem.providedBy(obj)

    # Event related
    def is_event(self, obj):
        return IATEvent.providedBy(obj)

    # File related
    def is_file(self, obj):
        return IATFile.providedBy(obj)

    def file_info(self, obj):
        context = aq_inner(obj)
        field = context.getField('file')
        fl = field.get(context)
        size = fl.get_size() or fl and len(fl) or 0
        return {
            'icon': fl.getBestIcon() or None,
            'filename': fl.filename or None,
            'content_type': context.lookupMime(field.getContentType(context)),
            'size': '%sKb' % (size / 1024)
        }

    # Link related
    def is_link(self, obj):
        return IATLink.providedBy(obj)

    def embed_code(self, obj):
        if self.is_link(obj):
            context = aq_inner(obj)
            return context.getField('embedCode').get(context)
        return None

    def formatPerex(self, text):
        max = self.context.getField('perex_length').get(self.context)
        view = getMultiAdapter((self.context, self.request), name=u'plone')
        return view.cropText(text, max)
    
    def sharing_services(self, item_url, title):
        services = self.context.getField('enable_sharing').get(self.context)
        result = []
        
        for service in services:
            if service in SHARING_PROVIDERS.keys():
                s_url = Template(SHARING_PROVIDERS[service]['url']).safe_substitute(url=item_url, title=title)
                result.append(dict(
                    id=service,
                    logo=SHARING_PROVIDERS[service]['logo'],
                    url=s_url)
                )
        return result
