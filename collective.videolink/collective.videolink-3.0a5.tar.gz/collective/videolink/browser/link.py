from p4a.videoembed.interfaces import IVideoMetadataRetriever
from p4a.videoembed.interfaces import IEmbedCodeConverterRegistry
import urllib2
from collective.videolink.utility import add_thumbnail
from Acquisition import aq_inner

from Products.Five.browser import BrowserView
from zope.component import getUtility
from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile

try:
    from collective.flowplayer.interfaces import IVideo
    from collective.flowplayer.interfaces import IAudio
    HAS_FLOWPLAYER = True
except ImportError:
    HAS_FLOWPLAYER = False

class VideoLink(BrowserView):
    """ Default view for links with awareness for videos

        Check if the context is a video link from known provider
        or a flowplayer resource.
        If not, just fall back to default view
    """

    index = ViewPageTemplateFile("embed.pt")

    def __init__(self, context, request):
        BrowserView.__init__(self, context, request)
        self.metadata_retriever = getUtility(IVideoMetadataRetriever)
        self.embedcode_converter = getUtility(IEmbedCodeConverterRegistry)

    def metadata(self):
        return self.metadata_retriever.get_metadata(self.context.getRemoteUrl())


    # FIXME add annotation so that it doesn't go there everytime
    def thumbnail(self):
        return add_thumbnail(self.context,'non event')

    def embedcode(self):
        return self.embedcode_converter.get_code(self.context.getRemoteUrl(), 400)

#    @property
    def _view(self):
        context_here = aq_inner(self.context)
        traverse_view =  context_here.restrictedTraverse
        if HAS_FLOWPLAYER and (IVideo.providedBy(self.context) or
                               IAudio.providedBy(self.context)):
            return traverse_view('flowplayer')
        elif not self.embedcode():
            link = traverse_view('link_redirect_view')
            return link()
        else:
            return self.index()

    def __call__(self, *args, **kwargs):
        return self._view()
