from base import TestCase
from Testing.makerequest import makerequest

class TestAuthoringProject(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def _makeOne(self):
        self.portal.invokeFactory('AuthoringProject', id='authoring')
        project = self.portal['authoring']
        add_view = project.restrictedTraverse('add-new-authoringproject')
        add_view('test')
        return project

    def testBasicCreate(self):
        project = self._makeOne()
        ids = project.objectIds()
        self.assertEqual('contents' in ids, True)
        self.assertEqual('templates' in ids, True)
        self.assertEqual('conversions' in ids, True)

    def testImportResourceTest(self):
        project = self._makeOne()
        project.restrictedTraverse('@@add-new-authoringproject')('new-project')
        template = project['templates']['template']
        view = template.restrictedTraverse('@@import_resource')
        view('pp-default', import_mode='clear')

    def testConversion(self):
        project = self._makeOne()
        conversion = project['conversions']['test']
        view = conversion.restrictedTraverse('@@generate_pdf')
        view()
        files_in_drafts = project.conversions.test.drafts.objectIds()
        self.assertEqual(len(files_in_drafts), 1)
        self.assertEqual(files_in_drafts[0].endswith('.pdf'), True)

    def testGenerateAll(self):
        self.portal = makerequest(self.portal) # we need SESSION
        project = self._makeOne()
        conversion = project['conversions']['test']
        view = conversion.restrictedTraverse('@@generate_html_pdf')
        view(html_mode='complete')

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestAuthoringProject))
    return suite
