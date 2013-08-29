from time import time

from zope.interface import implements
from zope.component import getMultiAdapter
from zope import schema
from zope.formlib import form
from zope.i18nmessageid import MessageFactory

from plone.app.vocabularies.catalog import SearchableTextSourceBinder
from plone.portlets.interfaces import IPortletDataProvider
from plone.app.portlets.portlets import base
from plone.app.form.widgets.uberselectionwidget import UberSelectionWidget
from plone.memoize import instance, ram

from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from Products.CMFCore.utils import getToolByName

from collective.blogging import HAS_LINGUA_PLONE
from collective.blogging import _
from collective.blogging.interfaces import IBlog, IEntryMarker

PLMF = MessageFactory('plonelocales')

def _cachekey(method,self):
    blog = self.data.target_blog
    lang = self.request.get('LANGUAGE', 'en')
    hour = lambda *args: time() // (60 * 60)
    return hash((blog, lang, hour))

class IArchivePortlet(IPortletDataProvider):
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
    
    extend_title = schema.Bool(
        title=_(u"Extend title"),
        description=_(u"Tick the checkbox to extend portlet title with target blog's title."),
        required=False,
        default=False,
    )


class Assignment(base.Assignment):
    """Portlet assignment.

    This is what is actually managed through the portlets UI and associated
    with columns.
    """

    implements(IArchivePortlet)

    target_blog = None
    extend_title = False
    
    def __init__(self, target_blog=None, extend_title=False):
        self.target_blog = target_blog
        self.extend_title = extend_title
    
    @property
    def title(self):
        """This property is used to give the title of the portlet in the
        "manage portlets" screen. Here, we use the title that the user gave.
        """
        blog_title = self.target_blog and self.target_blog.title()
        return _(u"Blog Archive: ${blog}", mapping={'blog':blog_title})


class Renderer(base.Renderer):
    """Portlet renderer.

    This is registered in configure.zcml. The referenced page template is
    rendered, and the implicit variable 'view' will refer to an instance
    of this class. Other methods can be added and referenced in the template.
    """

    render = ViewPageTemplateFile('archive.pt')
    
    def __init__(self, *args):
        base.Renderer.__init__(self, *args)
        self.portal_state = getMultiAdapter((self.context, self.request), name=u'plone_portal_state')
        self.tools = getMultiAdapter((self.context, self.request), name=u'plone_tools')

    def update(self):
        self.extend_title = self.data.extend_title

    @property
    def blog_url(self):
        blog = self.blog()
        if blog is not None:
            return blog.absolute_url()
            
    @property
    def blog_title(self):
        return self.blog() and self.blog().title
    
    @ram.cache(_cachekey)
    def archives(self):
        ts = getToolByName(self.context, 'translation_service')
        catalog = self.tools.catalog()
        entries = catalog(
            object_provides=IEntryMarker.__identifier__,
            path='/'.join(self.blog().getPhysicalPath()),
        )
        
        
        base_url = '%s?publish_year=' % self.blog_url
        archives = {}
        for entry in entries:
            year = archives.get(entry.publish_year, {'count':0, 'entries':{}})
            month = year['entries'].get(entry.publish_month, 0)
            
            year['entries'][entry.publish_month] = month + 1
            year['count'] = year['count'] + 1
            archives[entry.publish_year] = year
        
        # sort months and add year counts
        result = []
        for archive in archives.keys():
            year_url = '%s%s' % (base_url, archive)
            result.append({
                'year'  : archive,
                'count' : archives[archive]['count'],
                'url'   : year_url,
                'months': sorted([(m, c, '%s&publish_month=%s' % (year_url, m), PLMF(ts.month_msgid(m), default=ts.month_english(m))) \
                                    for m,c in archives[archive]['entries'].items()], reverse=True)
            })
        return sorted(result, reverse=True)
    
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


class AddForm(base.AddForm):
    """Portlet add form.
    
    This is registered in configure.zcml. The form_fields variable tells
    zope.formlib which fields to display. The create() method actually
    constructs the assignment that is being added.
    """
    form_fields = form.Fields(IArchivePortlet)
    form_fields['target_blog'].custom_widget = UberSelectionWidget
    
    label = _(u"Add Blog Archive portlet")
    description = _(u"This displays blog archives.")

    def create(self, data):
        return Assignment(**data)

class EditForm(base.EditForm):
    """Portlet edit form.
    
    This is registered with configure.zcml. The form_fields variable tells
    zope.formlib which fields to display.
    """

    form_fields = form.Fields(IArchivePortlet)
    form_fields['target_blog'].custom_widget = UberSelectionWidget

    label = _(u"Edit Blog Archive portlet")
    description = _(u"This displays blog archives.")
