from zope.interface.declarations import implements
from wm.sampledata.interfaces import ISampleDataPlugin
from wm.sampledata.utils import addPortlet, getFileContent, IPSUM_PARAGRAPH,\
    deleteItems, eventAndReindex, doWorkflowTransitions, createImage
from plone.portlet.static.static import Assignment as StaticAssignment
from Products.CMFPlone.utils import _createObjectByType
from Products.CMFCore.utils import getToolByName
from wm.sampledata.utils import getRandomImage

class DemoContent(object):
    implements(ISampleDataPlugin)

    title = u"Demo Content"

    description = u"""Creates a document with an image and assigns a portlet
that displays contact information."""

    def generate(self, context):
        pageId = 'sample'
        
        #delete sample document if it exists
        deleteItems(context, pageId)
        
        #create it w/o security checks
        _createObjectByType('Document', context, id=pageId,
                            title=u"Sample Document",)
        page = context[pageId]
        
        #download image from lorempixel.com - force colour images from category nature
        imageId = 'sampleImage'
        deleteItems(context, imageId)
        createImage(context, imageId, getRandomImage(category='nature', gray=False),
                    title=u"Random Image",
                    description=u"Downloaded from lorempixel.com")
        
        text = '<img class="image-right" src="%s/@@images/image/mini" />' % imageId + \
            IPSUM_PARAGRAPH
        
        #mimetype makes tiny recognize the text as HTML
        page.setText(text, mimetype='text/html')

        #publish and reindex (needed to make it show up in the navigation) the page
        doWorkflowTransitions(page)
        eventAndReindex(page)

        import wm.sampledata.example as myModule
        portlet = StaticAssignment(u"Contact", getFileContent(myModule, 'portlet.html'))
        addPortlet(page, 'plone.leftcolumn', portlet)
        
        