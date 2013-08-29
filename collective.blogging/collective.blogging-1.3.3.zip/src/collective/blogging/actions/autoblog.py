from OFS.SimpleItem import SimpleItem
from zope.component import adapts
from zope.schema import Bool
from zope.formlib import form
from zope.interface import Interface, implements

from plone.app.contentrules.browser.formhelper import NullAddForm
from plone.app.contentrules.browser.formhelper import AddForm, EditForm
from plone.contentrules.rule.interfaces import IRuleElementData, IExecutable

from Products.CMFPlone import PloneMessageFactory as _


class IAutoBlogAction(Interface):
    """Definition of the configuration
    """
    
    enable_blogging = Bool(
        title=_(u"Enable blogging"),
        description=_(u"If checked, action will mark content as blog or blog entry if supported."),
        required=False,
        default=False
    )
    
    exclude_from_nav = Bool(
        title=_(u"Exclude from navigation"),
        description=_(u"If checked, action will set content to be excluded from navigation."),
        required=False,
        default=False
    )
    
    enable_comments = Bool(
        title=_(u"Enable comments"),
        description=_(u"If checked, action will set content to allow comments."),
        required=False,
        default=False
    )

    set_entry_layout = Bool(
        title=_(u"Set layout to entry-view"),
        description=_(u"If checked, new blog item will use entry-view template layout."),
        required=False,
        default=True
    )


class AutoBlogAction(SimpleItem):
    """
    The implementation of the action defined before
    """
    implements(IAutoBlogAction, IRuleElementData)
    
    enable_blogging = False
    exclude_from_nav = False
    enable_comments = False
    set_entry_layout = False
    element = 'collective.blogging.actions.AutoBlog'

    @property
    def summary(self):
        return _(u"Enable auto-blogging")

class AutoBlogActionExecutor(object):
    """The executor for this action.
    """
    implements(IExecutable)
    adapts(Interface, IAutoBlogAction, Interface)

    def __init__(self, context, element, event):
        self.context = context
        self.element = element
        self.event = event

    def __call__(self):
        obj = self.event.object
        
        if self.element.enable_blogging:
            blog_field = obj.getField('blog_folder')
            entry_field = obj.getField('blog_entry')
            if blog_field:
                blog_field.set(obj, True)
        
            if entry_field:
                entry_field.set(obj, True)
        
        if self.element.exclude_from_nav:
            obj.setExcludeFromNav(True)
        
        if self.element.enable_comments:
            obj.allowDiscussion(True)

        if self.element.set_entry_layout:
            obj.setLayout('entry-view')
        
        return True


class AutoBlogAddForm(NullAddForm):
    """A degenerate "add form"" for auto blog actions.
    """
    
    def create(self):
        return AutoBlogAction()

class AutoBlogAddForm(AddForm):
    """An add form for auto-blog rule actions.
    """
    form_fields = form.FormFields(IAutoBlogAction)
    label = _(u"Add Auto-Blog Action")
    description = _(u"An auto-blog action can initialize various attributes on new or existing content.")
    form_name = _(u"Configure properties")
    
    def create(self, data):
        a = AutoBlogAction()
        form.applyChanges(a, self.form_fields, data)
        return a

class AutoBlogEditForm(EditForm):
    """An edit form for auto-blog rule actions.
    
    Formlib does all the magic here.
    """
    form_fields = form.FormFields(IAutoBlogAction)
    label = _(u"Edit Auto-Blog Action")
    description = _(u"An auto-blog action can initialize various attributes on new or existing content.")
    form_name = _(u"Configure properties")
