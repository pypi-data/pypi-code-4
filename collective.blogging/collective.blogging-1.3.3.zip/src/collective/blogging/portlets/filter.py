import logging
from time import time
from zope.interface import implements
from zope.component import getMultiAdapter
from zope import schema
from zope.formlib import form

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.memoize import instance, ram, volatile

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

from collective.blogging import HAS_LINGUA_PLONE
from collective.blogging import _
from collective.blogging.interfaces import IBlog

logger = logging.getLogger('collective.blogging')

class IFilterPortlet(IPortletDataProvider):
    """A portlet

    It inherits from IPortletDataProvider because for this portlet, the
    data that is being rendered and the portlet assignment itself are the
    same.
    """
    
    target_blog = schema.Choice(
        title=_(u"Target blog"),
        description=_(u"Find the blog which will be this portlet used for."),
        required=True,
        source=SearchableTextSourceBinder(
            {'object_provides' : IBlog.__identifier__, 'blogged' : True},
            default_query='path:'
        )
    )

    
    filter_cache = schema.Int(
        title=_(u"label_filter_cache", default=u"Filter cache"),
        description = _(u"help_filter_cache", default = u"Enter number of minutes for which will be cached filter options in the blog toolbar."),
        required=True
    )
    
    enable_count = schema.Bool(
        title = _(u"label_enable_count", default = u"Display count"),
        description = _(u"help_enable_count", default = u"Tick to enable / disable blog contents count displaying."),
        required = False
    )
                              
class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IFilterPortlet)

    target_blog = None
    filter_cache = 60
    enable_count = False
    
    def __init__(self, target_blog=None, filter_cache=60, enable_count=False):
        self.target_blog = target_blog
        self.filter_cache = filter_cache
        self.enable_count = enable_count

    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen.
        """
        return _(u"Blog filter portlet")

class AddForm(base.AddForm):
    """Portlet add form.

    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IFilterPortlet)
    form_fields['target_blog'].custom_widget = UberSelectionWidget
    form_fields['filter_cache'].field.default = 60

    def create(self, data):
        return Assignment(**data)

def _filter_cachekey(method, self):
    """ Time and path based cache """
    path = self.data.target_blog
    interval = self.data.filter_cache
    if not interval:
        interval = 0

    if interval == 0:
        # Avoid ZeroDivisionError by raising a different error
        # that will be caught by plone.memoize
        raise volatile.DontCache

    return hash((path, time() // (60 * interval)))

class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('filter.pt')
    
    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        self.portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
    
    @property
    def available(self):
        return True
        
    @property
    def blog_url(self):
        blog = self.blog()
        if blog is not None:
            return blog.absolute_url()
            
    @property
    def show_count(self):
        return self.data.enable_count

    @instance.memoize
    def blog(self):
        """ Get the blog the portlet is pointing to """
        
        blog_path = self.data.target_blog
        if not blog_path:
            return None

        if blog_path.startswith('/'):
            blog_path = blog_path[1:]
        
        if not blog_path:
            return None
        portal = self.portal_state.portal()
        obj = portal.restrictedTraverse(blog_path, default=None)
        if HAS_LINGUA_PLONE:
            return obj.getTranslation()
        return obj
        
    def is_filtered(self):
        subject = self.request.get('Subject', [''])
        year = self.request.get('publish_year', '')
        month = self.request.get('publish_month', '')
        
        return not (subject[0]=='' and year=='' and month=='')

    @instance.memoize
    def contents(self):
        blog = self.blog()
        blog_view = getMultiAdapter((blog, self.request), name="blog-view")
        return blog_view.contents()

    @property
    def count(self):
        return len(self.contents())
        
    def filter_info(self):
        subject = self.request.get('Subject')
        year    = self.request.get('publish_year')
        month   = self.request.get('publish_month')

        info = self._filter_info()
        
        for filter in info:
            if filter['id']=='Subject:list':
                filter['selected'] = subject and subject != [''] and subject[0] or None
            elif filter['id']=='publish_year':
                filter['selected'] = year and int(year) or None
            elif filter['id']=='publish_month':
                filter['selected'] = month and int(month) or None


        return info
        
              
    @ram.cache(_filter_cachekey)
    def _filter_info(self):
        #logger.info('Caching filter info')
        
        subjects = set()
        years = set()
        months = set()

        for brain in self.contents():
            for s in brain.Subject:
                subjects.add(s)
            if brain.publish_year:
                years.add(brain.publish_year)
            if brain.publish_month:
                months.add(brain.publish_month)
        subjects = list(subjects)
        years = list(years)
        months = list(months)

        subjects.sort()
        years.sort()
        months.sort()

        return [
            {
                'id': 'Subject:list',
                'title': _(u'select_category_option', default=u'Category'),
                'options': subjects,
                'selected': None
            },
            {
                'id': 'publish_year',
                'title': _(u'select_year_option', default=u'Year'),
                'options': years,
                'selected': None
            },
            {
                'id': 'publish_month',
                'title': _(u'select_month_option', default=u'Month'),
                'options': months,
                'selected': None
            }
        ]


class EditForm(base.EditForm):
    """Portlet edit form.

    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """
    form_fields = form.Fields(IFilterPortlet)
    form_fields['target_blog'].custom_widget = UberSelectionWidget
