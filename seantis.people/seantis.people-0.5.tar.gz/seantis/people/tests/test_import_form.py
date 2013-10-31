from mock import patch, Mock

from z3c.form.interfaces import ActionExecutionError

from seantis.people import tests
from seantis.people.interfaces import IPerson


class MockFile(object):
    def __init__(self, filename, data):
        self.filename = filename
        self.data = data


class TestImportForm(tests.IntegrationTestCase):

    def test_import_form_fields(self):
        self.login('admin')

        new_type = self.new_temporary_type(
            title='employee',
            behaviors=[IPerson.__identifier__]
        )

        form = self.get_import_form()
        types = form.fields['portal_type'].field.vocabulary.by_token

        self.assertEqual(types['employee'].value, new_type.id)

    def test_import_format(self):
        form = self.get_import_form()

        self.assertEqual(form.get_format_from_filename('asdf'), '')
        self.assertEqual(form.get_format_from_filename('file.txt'), 'txt')
        self.assertEqual(form.get_format_from_filename('file.xls.bak'), 'bak')

    @patch('transaction.abort')
    def test_unsupported_format(self, abort):
        form = self.get_import_form()

        form.extractData = Mock(return_value=({
            'portal_type': '',
            'import_file': MockFile('test.jpg', None)
        }, None))

        self.assertRaises(
            ActionExecutionError, form.run_import.func, form, 'import'
        )
        self.assertTrue(abort.called)

    @patch('seantis.people.browser.import_form.import_people')
    def test_run_import(self, import_people):
        form = self.get_import_form()

        form.extractData = Mock(return_value=({
            'portal_type': '',
            'import_file': MockFile('test.csv', None)
        }, None))

        import_people.return_value = 3

        form.run_import.func(form, 'import')

        self.assertEqual(form.status.mapping['count'], 3)
