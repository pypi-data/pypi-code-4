from unittest import TestCase
from mock import Mock, patch
from ming.odm import ThreadLocalORMSession

from allura.tests import TestController
from allura.tests.decorators import with_wiki
from allura import model as M

from googlecodewikiimporter.importer import (
        GoogleCodeWikiImporter,
        GoogleCodeWikiComment,
        GoogleCodeWikiPage,
        GoogleCodeWikiImportController,
        GoogleCodeWikiExtractor,
        )


class TestGoogleCodeWikiComment(TestCase):
    def _makeOne(self, html=None):
        from BeautifulSoup import BeautifulSoup

        html = html or '''
        <div class="artifactcomment">
          <span class="author">Comment by  project member 
              <a class="userlink" href="/u/testuser/">testuser</a>,
          </span>
          <span class="date" title="Mon Jun 17 08:05:30 2013">Jun 17, 2013</span>
          <div>
            <div class="commentcontent">
              <p>Hey, this is my comment.</p>
            </div>
          </div>
        </div>
        '''
        return GoogleCodeWikiComment(BeautifulSoup(html))

    def test__author(self):
        c = self._makeOne()
        self.assertEqual(c._author.text, u'testuser')
        c = self._makeOne('''
            <span class="author">
                <span class="userlink">testuser</a>
            </span>''')
        self.assertEqual(c._author.text, u'testuser')

    def test_author_name(self):
        c = self._makeOne()
        self.assertEqual(c.author_name, u'testuser')

    def test_author_link(self):
        c = self._makeOne()
        self.assertEqual(c.author_link, 'http://code.google.com/u/testuser/')
        c = self._makeOne('''
            <span class="author">
                <span class="userlink">testuser</a>
            </span>''')
        self.assertEqual(c.author_link, None)

    def test_text(self):
        c = self._makeOne()
        self.assertEqual(c.text.strip(), u"Hey, this is my comment.")

    def test_annotated_text(self):
        c = self._makeOne()
        self.assertEqual(c.annotated_text.strip(),
            u'Originally posted by: [testuser](http://code.google.com/u/testuser/)\n'
            '\n'
            'Hey, this is my comment.')

        c = self._makeOne('''
        <div class="artifactcomment">
          <span class="author">Comment by  project member 
              <span class="userlink">testuser</span>,
          </span>
          <span class="date" title="Mon Jun 17 08:05:30 2013">Jun 17, 2013</span>
          <div>
            <div class="commentcontent">
              <p>Hey, this is my comment.</p>
            </div> 
          </div>
        </div>
        ''')
        self.assertEqual(c.annotated_text.strip(),
            'Originally posted by: testuser\n'
            '\n'
            'Hey, this is my comment.')

    def test_timestamp(self):
        from datetime import datetime
        c = self._makeOne()
        self.assertEqual(c.timestamp, datetime(2013, 6, 17, 8, 5, 30))


class TestGoogleCodeWikiPage(TestCase):
    HTML = '''
    <div id="maincol">
      <div id="wikipage">
        <table>
          <tbody><tr>
            <td style="vertical-align:top; padding-left:5px">
              <div id="wikiheader">
                <span style="font-size:120%;font-weight:bold">MyPage</span>
                <div>
                  <i>Page description</i>
                  <br>
                  <a class="label" href="/p/mypage/w/list?q=label:MyLabel" title="MyLabel">MyLabel</a>
                  <div id="wikiauthor">
                    Updated <span title="Sat Jul 6 06:40:08 2013">Jul 6, 2013</span>
                    by <a class="userlink" href="/u/testauthor/">testauthor</a>
                  </div>
                </div>
              </div>
              <div id="wikicontent">
                <div class="vt" id="wikimaincol">
                  <h1>Main Heading</h1>
                  <p>This is a test</p>
                  <p>This is a link to <a href="/p/myproject/wiki/AnotherPage">AnotherPage</a></p>
                  <p>Link to <a href="http://example.com">another site</a><br/>
                  Intra-project issue link: <a href="/p/myproject/issues/detail?id=1">issue 1</a><br/>
                  Inter-project issue link: <a href="/p/otherproject/issues/detail?id=1">issue 1</a><br/>
                  Intra-project source link: <a href="/p/myproject/source/detail?r=1">r1</a><br/>
                  Inter-project source link: <a href="/p/otherproject/source/detail?r=1">r1</a></p>
                </div>
              </div>
            </td></tr>
          <tr></tr>
          </tbody>
        </table>
      </div>
      <div id="wikicommentcol">
        <div class="collapse">
          <div id="commentlist">
            <div class="artifactcomment">
              <span class="author">Comment by
                <a class="userlink" href="/u/testcommenter/">testcommenter</a>,
              </span>
              <span class="date" title="Fri Apr 25 15:08:06 2008">Apr 25, 2008</span>
              <div>
                <div class="commentcontent">
                  <p>A test comment.</p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
    '''

    def _makeOne(self):
        with patch('googlecodewikiimporter.importer.urllib2.urlopen') as urlopen:
            urlopen.return_value = self.HTML
            return GoogleCodeWikiPage('MyPage', 'http://code.google.com/p/myproject/wiki/MyPage', 'myproject')

    def test_rewrite_wiki_links(self):
        s = '[Page One](/p/myproject/wiki/PageOne) [External](http://example.com)'
        importer = self._makeOne()
        self.assertEqual(importer.rewrite_wiki_links(s),
                '[Page One](PageOne) [External](http://example.com)')

    def test_text(self):
        p = self._makeOne()
        self.assertEqual(p.text.strip(), u'''\
# Main Heading

This is a test

This is a link to [AnotherPage](AnotherPage)

Link to [another site](http://example.com)  
Intra-project issue link: [issue 1](#1)  
Inter-project issue link: [issue 1](https://code.google.com/p/otherproject/issues/detail?id=1)  
Intra-project source link: [r1]  
Inter-project source link: [r1](https://code.google.com/p/otherproject/source/detail?r=1)''')

    def test_timestamp(self):
        from datetime import datetime
        p = self._makeOne()
        self.assertEqual(p.timestamp, datetime(2013, 7, 6, 6, 40, 8))

    def test_labels(self):
        p = self._makeOne()
        self.assertEqual(p.labels, ['MyLabel'])

    def test_author(self):
        p = self._makeOne()
        self.assertEqual(p.author, 'testauthor')

    def test_comments(self):
        p = self._makeOne()
        self.assertEqual(len(p.comments), 1)
        self.assertIsInstance(p.comments[0], GoogleCodeWikiComment)


class TestGoogleCodeWikiImporter(TestCase):
    @patch('googlecodewikiimporter.importer.M')
    @patch('googlecodewikiimporter.importer.WM.Page')
    @patch('googlecodewikiimporter.importer.h.push_context')
    @patch('googlecodewikiimporter.importer.g')
    @patch('googlecodewikiimporter.importer.c')
    @patch('googlecodewikiimporter.importer.GoogleCodeWikiExtractor')
    @patch('googlecodewikiimporter.importer.GoogleCodeWikiPage')
    def test_import_tool(self, wp, extractor, c, g, push_context, Page, M):
        project, user = Mock(), Mock()
        extractor.return_value.get_wiki_pages.return_value = [('name', 'url')]
        extractor.return_value.get_default_wiki_page_name.return_value = None
        extractor.gc_project_name = 'testproject'
        wp.return_value.name = 'name'
        c.app = project.install_app.return_value
        c.app.config.options.mount_point = 'wiki'
        c.app.config.options.import_id = {
                'source': 'Google Code',
                'project_name': 'testproject',
            }
        c.app.config.options.get = lambda *a: getattr(c.app.config.options, *a)
        c.app.url = 'foo'
        GoogleCodeWikiImporter().import_tool(project, user, project_name='testproject')
        extractor.assert_called_once_with('testproject')
        project.install_app.assert_called_once_with('Wiki',
                mount_point='wiki',
                mount_label='Wiki',
                import_id={
                        'source': 'Google Code',
                        'project_name': 'testproject',
                    },
            )
        self.assertEqual(Page.upsert.call_count, 1)
        self.assertEqual(Page.upsert.return_value.import_id, {
                'source': 'Google Code',
                'project_name': 'testproject',
                'source_id': 'name',
            })
        self.assertEqual(Page.query.get.call_count, 1)
        self.assertEqual(Page.query.get.return_value.delete.call_count, 1)
        self.assertEqual(c.app.root_page_name, 'browse_pages')
        M.AuditLog.log.assert_called_once_with(
                'import tool wiki from testproject on Google Code',
                project=project,
                user=user,
                url='foo',
            )
        g.post_event.assert_called_once_with('project_updated')

    @patch('googlecodewikiimporter.importer.h')
    @patch('googlecodewikiimporter.importer.GoogleCodeWikiExtractor')
    def test_import_tool_failure(self, GoogleCodeWikiExtractor, h):
        project = Mock()
        user = Mock()
        app = project.install_app.return_value
        h.push_context.side_effect = ValueError
        self.assertRaises(ValueError, GoogleCodeWikiImporter().import_tool, project, user, project_name='testproject')
        h.make_app_admin_only.assert_called_once_with(app)

    @patch('googlecodewikiimporter.importer.M')
    @patch('googlecodewikiimporter.importer.WM.Page')
    @patch('googlecodewikiimporter.importer.h.push_context')
    @patch('googlecodewikiimporter.importer.g')
    @patch('googlecodewikiimporter.importer.c')
    @patch('googlecodewikiimporter.importer.GoogleCodeWikiExtractor')
    @patch('googlecodewikiimporter.importer.GoogleCodeWikiPage')
    def test_import_tool_default_page(self, wp, extractor, c, g, push_context, Page, M):
        project, user = Mock(), Mock()
        extractor.return_value.get_wiki_pages.return_value = [('Home', 'url'), ('name', 'url2'), ('other', 'url3')]
        extractor.return_value.get_default_wiki_page_name.return_value = 'name'
        extractor.gc_project_name = 'testproject'
        def named_mock(name):
            nm = Mock(comments=[])
            nm.name = name  # Mock(name='foo') doesn't do what you think :-(
            return nm
        wp.side_effect = lambda n,u,pn: named_mock(n)
        c.app = project.install_app.return_value
        c.app.config.options.mount_point = 'wiki'
        c.app.config.options.import_id = {
                'source': 'Google Code',
                'project_name': 'testproject',
            }
        c.app.config.options.get = lambda *a: getattr(c.app.config.options, *a)
        c.app.url = 'foo'
        GoogleCodeWikiImporter().import_tool(project, user, project_name='testproject')
        self.assertEqual(Page.query.get.call_count, 0)
        self.assertEqual(c.app.root_page_name, 'name')



class TestGoogleCodeWikiImportController(TestController, TestCase):
    def setUp(self):
        """Mount Google Code importer on the SVN admin controller"""
        super(TestGoogleCodeWikiImportController, self).setUp()
        from forgewiki.wiki_main import WikiAdminController
        WikiAdminController._importer = GoogleCodeWikiImportController()

    @with_wiki
    def test_index(self):
        r = self.app.get('/p/test/admin/wiki/_importer/')
        self.assertIsNotNone(r.html.find(attrs=dict(name="gc_project_name")))
        self.assertIsNotNone(r.html.find(attrs=dict(name="mount_label")))
        self.assertIsNotNone(r.html.find(attrs=dict(name="mount_point")))

    @with_wiki
    @patch('forgeimporters.base.import_tool')
    def test_create(self, import_tool):
        params = dict(gc_project_name='myproject',
                mount_label='mylabel',
                mount_point='mymount',
                )
        r = self.app.post('/p/test/admin/wiki/_importer/create', params,
                status=302)
        self.assertEqual(r.location, 'http://localhost/p/test/admin/')
        self.assertEqual(u'mymount', import_tool.post.call_args[1]['mount_point'])
        self.assertEqual(u'mylabel', import_tool.post.call_args[1]['mount_label'])
        self.assertEqual(u'myproject', import_tool.post.call_args[1]['project_name'])

    @with_wiki
    @patch('forgeimporters.base.import_tool')
    def test_create_limit(self, import_tool):
        project = M.Project.query.get(shortname='test')
        project.set_tool_data('GoogleCodeWikiImporter', pending=1)
        ThreadLocalORMSession.flush_all()
        params = dict(gc_project_name='myproject',
                mount_label='mylabel',
                mount_point='mymount',
                )
        r = self.app.post('/p/test/admin/wiki/_importer/create', params,
                status=302).follow()
        self.assertIn('Please wait and try again', r)
        self.assertEqual(import_tool.post.call_count, 0)


class TestGoogleCodeWikiExtractor(TestCase):

    def _make_extractor(self, html, url='http://code.google.com/p/my-project/w/list'):
        from BeautifulSoup import BeautifulSoup
        extractor = GoogleCodeWikiExtractor('my-project')
        extractor._page_cache = {url: BeautifulSoup(html)}
        return extractor

    def test_get_wiki_pages(self):
        extractor = self._make_extractor('''
        <div id="resultstable">
            <a href="#">Link that's not a wiki page</a>
            <a href="/p/my-project/wiki/PageOne">PageOne</a>
        </div>''')
        self.assertEqual(list(extractor.get_wiki_pages()), [
            ('PageOne', 'http://code.google.com/p/my-project/wiki/PageOne')])

    def test_get_default_wiki_page_name(self):
        extractor = self._make_extractor('''
        <div id="mt">
            <a href="/p/my-project/wiki/MyHomePage#with_anchor?and_query_string" class="tab active">Wiki</a>
        </div>''')
        self.assertEqual(extractor.get_default_wiki_page_name(), 'MyHomePage')

    def test_get_default_wiki_page_name_no_link(self):
        extractor = self._make_extractor('''
        <div id="mt">
        </div>''')
        self.assertEqual(extractor.get_default_wiki_page_name(), None)

    def test_get_default_wiki_page_name_no_list(self):
        extractor = self._make_extractor('''
        <div id="mt">
            <a href="/p/my-project/w/list#with_anchor?and_query_string" class="tab active">Wiki</a>
        </div>''')
        self.assertEqual(extractor.get_default_wiki_page_name(), None)
