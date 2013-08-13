from zope.component import getUtility, getMultiAdapter

from plone.portlets.interfaces import IPortletType
from plone.portlets.interfaces import IPortletManager
from plone.portlets.interfaces import IPortletAssignment
from plone.portlets.interfaces import IPortletDataProvider
from plone.portlets.interfaces import IPortletRenderer

from plone.app.portlets.storage import PortletAssignmentMapping

from collective.portlet.explore import explorerportlet

from collective.portlet.explore.tests.base import TestCase

class TestPortlet(TestCase):

    def test_portlet_type_registered(self):
        portlet = getUtility(IPortletType,
                name='collective.portlet.explore.ExplorerPortlet')
        self.assertEquals(portlet.addview,
                'collective.portlet.explore.ExplorerPortlet')

    def test_interfaces(self):
        portlet = explorerportlet.Assignment()
        self.failUnless(IPortletAssignment.providedBy(portlet))
        self.failUnless(IPortletDataProvider.providedBy(portlet.data))

    def test_invoke_add_view(self):
        portlet = getUtility(IPortletType, name='collective.portlet.explore.ExplorerPortlet')
        mapping = self.portal.restrictedTraverse('++contextportlets++plone.leftcolumn')
        for m in mapping.keys():
            del mapping[m]
        addview = mapping.restrictedTraverse('+/' + portlet.addview)

        addview.createAndAdd(data=dict(name="name",
                                       root="root",
                                       currentFolderOnly="currentFolderOnly",
                                       topLevel="topLevel",
                                       bottomLevel="bottomLevel"))

        self.assertEquals(len(mapping), 1)
        assignment=mapping.values()[0]
        self.failUnless(isinstance(assignment, explorerportlet.Assignment))
        self.assertEqual(assignment.name, "name")
        self.assertEqual(assignment.root, "root")
        self.assertEqual(assignment.currentFolderOnly, "currentFolderOnly")
        self.assertEqual(assignment.topLevel, "topLevel")
        self.assertEqual(assignment.bottomLevel, "bottomLevel")


    def test_obtain_renderer(self):
        context = self.folder
        request = self.folder.REQUEST
        view = self.folder.restrictedTraverse('@@plone')
        manager = getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = explorerportlet.Assignment()

        renderer = getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)
        self.failUnless(isinstance(renderer, explorerportlet.Renderer))


class TestRenderer(TestCase):

    def renderer(self, context=None, request=None, view=None, manager=None, assignment=None):
        context = context or self.folder
        request = request or self.folder.REQUEST
        view = view or self.folder.restrictedTraverse('@@plone')
        manager = manager or getUtility(IPortletManager, name='plone.rightcolumn', context=self.portal)

        assignment = assignment or explorerportlet.Assignment()
        return getMultiAdapter((context, request, view, manager, assignment), IPortletRenderer)

    def test_render(self):
        r = self.renderer(context=self.portal, assignment=explorerportlet.Assignment(topLevel=0))
        r = r.__of__(self.portal)
        r.update()
        output = r.render()
        self.assertEqual(output.count("navTreeItem"), 3)
        self.failUnless("node-%s" % self.portal.events.UID() in output)
        self.failUnless("node-%s" % self.portal.news.UID() in output)
        self.failUnless("node-%s" % self.portal.Members.UID() in output)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestPortlet))
    suite.addTest(makeSuite(TestRenderer))
    return suite
