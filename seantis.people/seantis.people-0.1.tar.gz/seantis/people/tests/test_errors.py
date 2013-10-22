from seantis.people import _
from seantis.people import errors, tests


class TestErrors(tests.IntegrationTestCase):

    def test_error_translation(self):
        err = errors.TranslatableException(_(u'Test'))
        self.assertEqual(err.translate(self.request), u'Test')

        err = errors.ContentImportError(_(u'Test'))
        self.assertEqual(err.translate(self.request), u'Test')

        err.colname = 'test'
        self.assertEqual(err.translate(self.request), u'Test (Column test)')

        err.rownumber = 1
        self.assertEqual(
            err.translate(self.request), u'Test (Row 1, Column test)'
        )
