from Products.CMFCore.utils import getToolByName
from collective.base.interfaces import IAdapter
from collective.base.tests.base import IntegrationTestCase
from plone.app.testing import TEST_USER_ID
from plone.app.testing import setRoles

import mock


class TestCase(IntegrationTestCase):
    """TestCase for Plone setup."""

    def test_create_atcontent(self):
        from Products.ATContentTypes.content.document import ATDocument
        self.assertIsInstance(self.create_atcontent('Document', id='doc'), ATDocument)

    def test_instance(self):
        from collective.base.adapter import Adapter
        self.assertIsInstance(IAdapter(self.portal), Adapter)

    def test_verifyObject(self):
        from zope.interface.verify import verifyObject
        self.assertTrue(verifyObject(IAdapter, IAdapter(self.portal)))

    def test_catalog(self):

        base = IAdapter(self.portal)
        self.assertEqual(base.catalog(), getToolByName(self.portal, 'portal_catalog'))

    def test_context_path(self):
        base = IAdapter(self.portal)
        self.assertEqual(base.context_path(), '/plone')

    def test__get_brains__empty(self):
        from Products.ATContentTypes.interfaces.folder import IATFolder
        base = IAdapter(self.portal)

        query = {}

        self.assertEqual(len(base.get_brains(**query)), 0)
        self.assertEqual(len(base.get_objects(**query)), 0)
        self.assertEqual(len(base.get_content_listing(**query)), 0)
        self.assertIsNone(base.get_brain(**query))
        self.assertIsNone(base.get_object(**query))

        self.assertEqual(len(base.get_brains(interfaces=IATFolder, **query)), 0)
        self.assertEqual(len(base.get_objects(interfaces=IATFolder, **query)), 0)
        self.assertEqual(len(base.get_content_listing(interfaces=IATFolder, **query)), 0)
        self.assertIsNone(base.get_brain(interfaces=IATFolder, **query))
        self.assertIsNone(base.get_object(interfaces=IATFolder, **query))

    def test__one_folder(self):
        """Add folder under portal."""
        from Products.ATContentTypes.interfaces.folder import IATFolder
        base = IAdapter(self.portal)

        folder1 = self.portal[self.portal.invokeFactory('Folder', 'folder1')]
        folder1.reindexObject()

        query = {}

        self.assertEqual(len(base.get_brains(**query)), 1)
        self.assertEqual(len(base.get_objects(**query)), 1)
        self.assertEqual(len(base.get_content_listing(**query)), 1)
        self.assertEqual(base.get_brain(**query).id, 'folder1')
        self.assertEqual(base.get_object(**query).id, 'folder1')

        self.assertEqual(len(base.get_brains(interfaces=IATFolder, **query)), 1)
        self.assertEqual(len(base.get_objects(interfaces=IATFolder, **query)), 1)
        self.assertEqual(len(base.get_content_listing(interfaces=IATFolder, **query)), 1)
        self.assertEqual(base.get_brain(interfaces=IATFolder, **query).id, 'folder1')
        self.assertEqual(base.get_object(interfaces=IATFolder, **query).id, 'folder1')

        query = {'path': '/'.join(folder1.getPhysicalPath())}

        self.assertEqual(len(base.get_brains(**query)), 1)
        self.assertEqual(len(base.get_objects(**query)), 1)
        self.assertEqual(len(base.get_content_listing(**query)), 1)
        self.assertEqual(base.get_brain(**query).id, 'folder1')
        self.assertEqual(base.get_object(**query).id, 'folder1')

        self.assertEqual(len(base.get_brains(interfaces=IATFolder, **query)), 1)
        self.assertEqual(len(base.get_objects(interfaces=IATFolder, **query)), 1)
        self.assertEqual(len(base.get_content_listing(interfaces=IATFolder, **query)), 1)
        self.assertEqual(base.get_brain(interfaces=IATFolder, **query).id, 'folder1')
        self.assertEqual(base.get_object(interfaces=IATFolder, **query).id, 'folder1')

        query['depth'] = 0
        self.assertEqual(len(base.get_brains(**query)), 1)
        self.assertEqual(len(base.get_objects(**query)), 1)
        self.assertEqual(len(base.get_content_listing(**query)), 1)
        self.assertEqual(base.get_brain(**query).id, 'folder1')
        self.assertEqual(base.get_object(**query).id, 'folder1')

        self.assertEqual(len(base.get_brains(interfaces=IATFolder, **query)), 1)
        self.assertEqual(len(base.get_objects(interfaces=IATFolder, **query)), 1)
        self.assertEqual(len(base.get_content_listing(interfaces=IATFolder, **query)), 1)
        self.assertEqual(base.get_brain(interfaces=IATFolder, **query).id, 'folder1')
        self.assertEqual(base.get_object(interfaces=IATFolder, **query).id, 'folder1')

        query['depth'] = 1
        self.assertEqual(len(base.get_brains(**query)), 0)
        self.assertEqual(len(base.get_objects(**query)), 0)
        self.assertEqual(len(base.get_content_listing(**query)), 0)
        self.assertIsNone(base.get_brain(**query))
        self.assertIsNone(base.get_object(**query))

        self.assertEqual(len(base.get_brains(interfaces=IATFolder, **query)), 0)
        self.assertEqual(len(base.get_objects(interfaces=IATFolder, **query)), 0)
        self.assertEqual(len(base.get_content_listing(interfaces=IATFolder, **query)), 0)
        self.assertIsNone(base.get_brain(interfaces=IATFolder, **query))
        self.assertIsNone(base.get_object(interfaces=IATFolder, **query))

        query['depth'] = 0
        self.assertEqual(len(base.get_brains(**query)), 1)
        self.assertEqual(len(base.get_objects(**query)), 1)
        self.assertEqual(len(base.get_content_listing(**query)), 1)
        self.assertEqual(base.get_brain(**query).id, 'folder1')
        self.assertEqual(base.get_object(**query).id, 'folder1')

        setRoles(self.portal, TEST_USER_ID, ['Member'])

        from plone.app.testing.helpers import logout
        logout()

        base = IAdapter(self.portal)
        self.assertEqual(len(base.get_brains(**query)), 0)

        query['unrestricted'] = True
        self.assertEqual(len(base.get_brains(**query)), 1)

    def test__two_folders(self):
        from Products.ATContentTypes.interfaces.folder import IATFolder
        base = IAdapter(self.portal)

        folder1 = self.portal[self.portal.invokeFactory('Folder', 'folder1')]
        folder1.reindexObject()
        folder2 = folder1[folder1.invokeFactory('Folder', 'folder2')]
        folder2.reindexObject()

        query = {}

        self.assertEqual(len(base.get_brains(**query)), 2)
        self.assertEqual(len(base.get_objects(**query)), 2)
        self.assertEqual(len(base.get_content_listing(**query)), 2)

        self.assertEqual(len(base.get_brains(interfaces=IATFolder, **query)), 2)
        self.assertEqual(len(base.get_objects(interfaces=IATFolder, **query)), 2)
        self.assertEqual(len(base.get_content_listing(interfaces=IATFolder, **query)), 2)

        query['sort_limit'] = 1
        self.assertEqual(len(base.get_brains(**query)), 1)
        self.assertEqual(len(base.get_objects(**query)), 1)
        self.assertEqual(len(base.get_content_listing(**query)), 1)

        self.assertEqual(len(base.get_brains(interfaces=IATFolder, **query)), 1)
        self.assertEqual(len(base.get_objects(interfaces=IATFolder, **query)), 1)
        self.assertEqual(len(base.get_content_listing(interfaces=IATFolder, **query)), 1)

    def test__folder_and_document(self):
        from Products.ATContentTypes.interfaces.document import IATDocument
        from Products.ATContentTypes.interfaces.folder import IATFolder
        base = IAdapter(self.portal)

        folder1 = self.portal[self.portal.invokeFactory('Folder', 'folder1')]
        folder1.reindexObject()
        doc1 = self.portal[self.portal.invokeFactory('Document', 'doc1')]
        doc1.reindexObject()

        self.assertEqual(len(base.get_brains(IATDocument)), 1)
        self.assertEqual(len(base.get_objects(IATDocument)), 1)
        self.assertEqual(len(base.get_content_listing(IATDocument)), 1)
        self.assertEqual(base.get_brain(IATDocument).id, 'doc1')
        self.assertEqual(base.get_object(IATDocument).id, 'doc1')

        self.assertEqual(len(base.get_brains([IATDocument, IATFolder])), 2)
        self.assertEqual(len(base.get_objects([IATDocument, IATFolder])), 2)
        self.assertEqual(len(base.get_content_listing([IATDocument, IATFolder])), 2)

        self.assertEqual(len(base.get_brains([IATDocument], object_provides=IATFolder.__identifier__)), 2)
        self.assertEqual(len(base.get_objects([IATDocument], object_provides=IATFolder.__identifier__)), 2)
        self.assertEqual(len(base.get_content_listing([IATDocument], object_provides=IATFolder.__identifier__)), 2)

    @mock.patch('collective.base.adapter.getToolByName')
    def test_getSessionData(self, getToolByName):
        from collective.base.interfaces import IAdapter
        IAdapter(self.portal).getSessionData()
        getToolByName().getSessionData.assert_called_with(create=True)

    def create_event(self, **kwargs):
        event = self.portal[self.portal.invokeFactory('Event', **kwargs)]
        event.reindexObject()
        return event

    def test_event_datetime(self):
        base = IAdapter(self.portal)

        from DateTime import DateTime
        self.create_event(id='event1', startDate=DateTime('2013/02/25'), endDate=DateTime('2013/02/25'))
        self.create_event(id='event2', startDate=DateTime('2013/02/26 20:00'), endDate=DateTime('2013/02/26 22:00'))
        self.create_event(id='event3', startDate=DateTime('2013/02/27'), endDate=DateTime('2013/02/28'))

        from Products.ATContentTypes.interfaces.event import IATEvent
        res = []
        for item in base.get_content_listing(IATEvent, sort_on='start'):
            res.append(base.event_datetime(item))
        try:
            self.assertEqual(res, [
                u'Feb 25, 2013 12:00 AM',
                u'Feb 26, 2013 08:00 PM - 10:00 PM',
                u'Feb 27, 2013 12:00 AM - Feb 28, 2013 12:00 AM'])
        except AssertionError:
            self.assertEqual(res, [
                u'2013-02-25 00:00',
                u'2013-02-26 20:00 - 22:00',
                u'2013-02-27 00:00 - 2013-02-28 00:00'])

    def test_portal(self):
        self.assertEqual(IAdapter(self.portal).portal(), self.portal)

    def test_portal_path(self):
        self.assertEqual(IAdapter(self.portal).portal_path(), '/plone')

    def test_membership(self):
        from Products.PlonePAS.tools.membership import MembershipTool
        adapter = IAdapter(self.portal)
        self.assertIsInstance(adapter.membership(), MembershipTool)
