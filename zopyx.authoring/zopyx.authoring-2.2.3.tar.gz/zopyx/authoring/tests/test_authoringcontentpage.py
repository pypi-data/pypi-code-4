from base import TestCase
from Testing.makerequest import makerequest

HTML = """
<html><body>
<div class="empty"></div>
<ul>
<li>item 1</li>
<li>item 2</li>
</body></html>
"""

class TestContentPage(TestCase):

    def afterSetUp(self):
        self.setRoles(('Manager',))

    def _makeOne(self):
        self.portal.invokeFactory('AuthoringProject', id='authoring')
        project = self.portal['authoring']
        add_view = project.restrictedTraverse('add-new-authoringproject')
        add_view('test')
        return project

    def testContentPageSubscribers(self):
        project = self._makeOne()
        project.restrictedTraverse('@@add-new-authoringproject')('new-project')
        content_folder = project['contents']['new-project']
        content_folder.invokeFactory('AuthoringContentPage', id='mycontent')
        page = content_folder['mycontent']
        self.assertEqual(page.portal_type, 'AuthoringContentPage')
        page.setText(HTML)
        page.setContentType('text/html')
        page.getField('text').setContentType(page, 'text/html')
        page.processForm()  # trigger subscriber
        html = page.getText()
        # empty div tags should be removed
        self.assertTrue('empty' not in html)
        # list tags should have id attributes
        self.assertTrue('<ul id="' in html)
        self.assertTrue('<li id="' in html)


def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(TestContentPage))
    return suite
