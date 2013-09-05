from plone.app.contentlisting.interfaces import IContentListing
from cs.folderishpage import MessageFactory as _
from five import grok
from plone.directives import dexterity, form

from plone.namedfile.interfaces import IImageScaleTraversable
from plone.app.textfield import RichText


# Interface class; used to define content-type schema.
class IFolderishPage(form.Schema, IImageScaleTraversable):
    """
    A folderish page
    """

    text = RichText(title=_(u'Content'),
                    required=False
        )


# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.
class FolderishPage(dexterity.Container):
    grok.implements(IFolderishPage)
    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# templates called folderishpageview.pt .
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# using grok.name below.
# This will make this view the default view for your content-type

grok.templatedir('templates')


class FolderishPageView(grok.View):
    grok.context(IFolderishPage)
    grok.require('zope2.View')
    grok.name('view')


class FolderishPageWithContents(grok.View):
    grok.context(IFolderishPage)
    grok.require('zope2.View')
    grok.name('contentsview')

    def contents(self):
        return IContentListing(self.context.getFolderContents())
