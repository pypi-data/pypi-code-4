import sys
import unittest

from zope.testing import doctestunit
from zope.component import testing
import zope.interface
import zope.component
from Testing import ZopeTestCase as ztc
from Acquisition import aq_base

from Products.Five import zcml
from Products.Five import BrowserView
from Products.Five import fiveconfigure
from Products.PloneTestCase import PloneTestCase as ptc
from Products.PloneTestCase.layer import PloneSite
from zope.app.testing import ztapi


ptc.setupPloneSite(products=['collective.videolink'])

import collective.videolink
from collective.videolink.browser.link import VideoLink

class TestCase(ptc.PloneTestCase):
    class layer(PloneSite):
        @classmethod
        def setUp(cls):
            fiveconfigure.debug_mode = True
            zcml.load_config('configure.zcml',
                             collective.videolink)
            fiveconfigure.debug_mode = False

        @classmethod
        def tearDown(cls):
            pass

try:
    from collective.flowplayer.interfaces import IVideo
except ImportError:
    # fake collective.flowplayer, if it is not there
    from collective.videolink import testifaces
    sys.modules['collective'] = testifaces
    sys.modules['collective.flowplayer'] = testifaces
    sys.modules['collective.flowplayer.interfaces'] = testifaces
    import collective.videolink.browser.link
    from collective.flowplayer.interfaces import IVideo
    from collective.flowplayer.interfaces import IAudio
    collective.videolink.browser.link.HAS_FLOWPLAYER = True
    collective.videolink.browser.link.IVideo = IVideo
    collective.videolink.browser.link.IAudio = IAudio

    class DummyView(BrowserView):

        __name__ = 'flowplayer'

class VideoLinkTestCase(TestCase):

    def test_portalfactory(self):
        link_type = self.portal.portal_types.Link
        assert link_type.immediate_view == 'embeddedvideo'
        assert link_type.default_view == 'embeddedvideo'
        assert 'embeddedvideo' in link_type.view_methods

    def test_standardlink(self):
        self.folder.invokeFactory('Link', 'openbsd')
        link = self.folder['openbsd']
        link.setRemoteUrl('http://www.openbsd.org')
        dispatcher = VideoLink(link, self.app.REQUEST)
        self.assertEqual(dispatcher._view.__name__, 'link_redirect_view')

    def test_embeddedlink(self):
        self.folder.invokeFactory('Link', 'yt')
        link = self.folder['yt']
        link.setRemoteUrl('http://www.youtube.com/watch?v=4cXHDoRttSY')
        dispatcher = VideoLink(link, self.app.REQUEST)
        self.assertEqual(aq_base(dispatcher._view).__name__, 'embed')

    def test_flowplayerlink(self):
        self.folder.invokeFactory('Link', 'fp')
        link = self.folder['fp']
        link.setRemoteUrl('http://www.example.org/myvideo.flv')
        zope.interface.alsoProvides(link, IVideo)
        if zope.component.queryMultiAdapter((link, self.app.REQUEST),
                                            name='flowplayer') == None:
            ztapi.browserView(zope.interface.Interface, "flowplayer", DummyView)
        dispatcher = VideoLink(link, self.app.REQUEST)
        self.assertEqual(dispatcher._view.__name__, 'flowplayer')

def test_suite():
    return unittest.TestSuite((
        unittest.makeSuite(VideoLinkTestCase),))

