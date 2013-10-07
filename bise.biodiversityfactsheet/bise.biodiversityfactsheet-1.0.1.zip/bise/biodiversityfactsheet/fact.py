from zope.component import getMultiAdapter
from Acquisition import aq_inner
from plone.app.contentlisting.interfaces import IContentListing
from zope.app.container.interfaces import IObjectAddedEvent
from five import grok
from plone.directives import dexterity, form
from plone.namedfile.interfaces import IImageScaleTraversable
from zope import schema
from zope.schema.vocabulary import SimpleVocabulary, SimpleTerm
from plone.app.textfield import RichText

from bise.biodiversityfactsheet import MessageFactory as _


fact_icons = SimpleVocabulary(
    [
     SimpleTerm(value=u'text', title=_(u'Text')),
     SimpleTerm(value=u'map', title=_(u'Map')),
     SimpleTerm(value=u'link', title=_(u'Link')),
     SimpleTerm(value=u'graph', title=_(u'Graph')),
     SimpleTerm(value=u'pdf', title=_(u'PDF')),
     ]
    )


# Interface class; used to define content-type schema.
class IFact(form.Schema, IImageScaleTraversable):
    """
    Factsheet content
    """

    text = RichText(
        title=_(u'Text'),
        description=_(u'Text of this fact'),
        required=False,
        )

    embed = schema.Text(
        title=_(u'Embed code'),
        description=_(u'Paste here content coming from external site. '
                      u'Such as iframe, object, or other external site code.'
            ),
        required=False,
        )

    webmapid = schema.Text(
        title=_(u'Webmap ID'),
        description=_(u'Webmap id(s) separated by commas'),
        required=False,
        )

    fact_icon = schema.Choice(
        title=_(u'Icon to show next to the title'),
        vocabulary=fact_icons,
        default=u'text',
        required=True
        )
    fact_source = RichText(
        title=_(u'Source'),
        description=_(u'Source'),
        required=True,
        )
    fact_year = schema.Text(
        title=_(u'Year'),
        description=_(u'Year'),
        required=True,
        )

# Custom content-type class; objects created for this content type will
# be instances of this class. Use this class to add content-type specific
# methods and properties. Put methods that are mainly useful for rendering
# in separate view classes.
class Fact(dexterity.Container):
    grok.implements(IFact)
    # Add your class methods and properties here


# View class
# The view will automatically use a similarly named template in
# templates called factview.pt .
# Template filenames should be all lower case.
# The view will render when you request a content object with this
# interface with "/@@view" appended unless specified otherwise
# using grok.name below.
# This will make this view the default view for your content-type
grok.templatedir('templates')


class FactView(grok.View):
    grok.context(IFact)
    grok.require('zope2.View')
    grok.name('view')

    def contents(self):
        context = aq_inner(self.context)
        contents = getMultiAdapter((context, self.request),
            name=u'factrenderview')()

        return contents


class FactRenderView(grok.View):
    grok.context(IFact)
    grok.require('zope2.View')
    grok.name('factrenderview')

    def files(self):
        context = aq_inner(self.context)
        files = context.getFolderContents({'portal_type': 'File'})
        return IContentListing(files)

    def links(self):
        context = aq_inner(self.context)
        links = context.getFolderContents({'portal_type': 'Link'})
        return IContentListing(links)

    def getMapIds(self):
        context = aq_inner(self.context)
        return context.webmapid.split(",")
        #return webmapid.split(",")


@grok.subscribe(IFact, IObjectAddedEvent)
def exclude_from_nav(context, event):
    context.exclude_from_nav = True