from unittest import TestCase
from mock import Mock, patch
from ming.odm import ThreadLocalORMSession

from allura.tests import TestController
from allura.tests.decorators import with_wiki
from allura import model as M

from tracwikiimporter.importer import (
    TracWikiImporter,
    TracWikiImportController,
    )


class TestTracWikiImporter(TestCase):

    @patch('tracwikiimporter.importer.AuditLog')
    @patch('tracwikiimporter.importer.session')
    @patch('tracwikiimporter.importer.tempfile.NamedTemporaryFile')
    @patch('tracwikiimporter.importer.g')
    @patch('tracwikiimporter.importer.WikiFromTrac')
    @patch('tracwikiimporter.importer.load_data')
    @patch('tracwikiimporter.importer.argparse.Namespace')
    @patch('tracwikiimporter.importer.WikiExporter')
    @patch('tracwikiimporter.importer.ApiTicket')
    @patch('tracwikiimporter.importer.datetime')
    def test_import_tool(self, dt, ApiTicket, WikiExporter, Namespace,
            load_data, WikiFromTrac, g, NamedTemporaryFile, session, AuditLog):
        from datetime import datetime, timedelta
        now = datetime.utcnow()
        dt.utcnow.return_value = now
        export_file = NamedTemporaryFile.return_value.__enter__.return_value
        export_file.name = '/my/file'

        importer = TracWikiImporter()
        app = Mock(name='ForgeWikiApp')
        app.config.options.mount_point = 'pages'
        app.url = 'foo'
        project = Mock(name='Project', shortname='myproject')
        project.install_app.return_value = app
        user = Mock(name='User', _id='id')
        res = importer.import_tool(project, user,
                mount_point='pages',
                mount_label='Pages',
                trac_url='http://example.com/trac/url')
        self.assertEqual(res, app)
        project.install_app.assert_called_once_with(
                'Wiki', mount_point='pages', mount_label='Pages',
                import_id={
                        'source': 'Trac',
                        'trac_url': 'http://example.com/trac/url/',
                    },
            )
        ApiTicket.assert_called_once_with(
                user_id=user._id,
                capabilities={"import": ["Projects", "myproject"]},
                expires=now + timedelta(minutes=60))
        WikiExporter.assert_called_once_with('http://example.com/trac/url/',
                Namespace.return_value)
        WikiExporter.return_value.export.assert_called_once_with(export_file)
        load_data.assert_called_once_with('/my/file',
                WikiFromTrac.parser.return_value, Namespace.return_value)
        AuditLog.log.assert_called_once_with(
                'import tool pages from http://example.com/trac/url/',
                project=project,
                user=user,
                url='foo',
            )
        g.post_event.assert_called_once_with('project_updated')

    @patch('tracwikiimporter.importer.session')
    @patch('tracwikiimporter.importer.ApiTicket')
    @patch('tracwikiimporter.importer.h')
    def test_import_tool_failure(self, h, ApiTicket, session):
        ApiTicket.side_effect = ValueError
        importer = TracWikiImporter()
        app = Mock(name='ForgeWikiApp')
        project = Mock(name='Project', shortname='myproject')
        project.install_app.return_value = app
        user = Mock(name='User', _id='id')
        self.assertRaises(ValueError, importer.import_tool,
                project, user,
                mount_point='pages',
                mount_label='Pages',
                trac_url='http://example.com/trac/url')
        h.make_app_admin_only.assert_called_once_with(app)


class TestTracWikiImportController(TestController, TestCase):
    def setUp(self):
        """Mount Trac import controller on the Wiki admin controller"""
        super(self.__class__, self).setUp()
        from forgewiki.wiki_main import WikiAdminController
        WikiAdminController._importer = TracWikiImportController()

    @with_wiki
    def test_index(self):
        r = self.app.get('/p/test/admin/wiki/_importer/')
        self.assertIsNotNone(r.html.find(attrs=dict(name="trac_url")))
        self.assertIsNotNone(r.html.find(attrs=dict(name="mount_label")))
        self.assertIsNotNone(r.html.find(attrs=dict(name="mount_point")))

    @with_wiki
    @patch('tracwikiimporter.importer.import_tool')
    def test_create(self, import_tool):
        params = dict(trac_url='http://example.com/trac/url',
                mount_label='mylabel',
                mount_point='mymount',
                )
        r = self.app.post('/p/test/admin/wiki/_importer/create', params,
                status=302)
        self.assertEqual(r.location, 'http://localhost/p/test/admin/')
        self.assertEqual(u'mymount', import_tool.post.call_args[1]['mount_point'])
        self.assertEqual(u'mylabel', import_tool.post.call_args[1]['mount_label'])
        self.assertEqual(u'http://example.com/trac/url', import_tool.post.call_args[1]['trac_url'])

    @with_wiki
    @patch('tracwikiimporter.importer.import_tool')
    def test_create_limit(self, import_tool):
        project = M.Project.query.get(shortname='test')
        project.set_tool_data('TracWikiImporter', pending=1)
        ThreadLocalORMSession.flush_all()
        params = dict(trac_url='http://example.com/trac/url',
                mount_label='mylabel',
                mount_point='mymount',
                )
        r = self.app.post('/p/test/admin/wiki/_importer/create', params,
                status=302).follow()
        self.assertIn('Please wait and try again', r)
        self.assertEqual(import_tool.post.call_count, 0)
