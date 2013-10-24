from mock import Mock

from z3c.form.interfaces import ActionExecutionError

from seantis.people import tests


class TestViewBase(tests.IntegrationTestCase):

    def test_form_parameters(self):
        form = self.get_import_form()

        form.extractData = Mock(return_value=('yo', None))
        self.assertEqual(form.parameters, 'yo')

        form.extractData = Mock(return_value=('yo', 'error'))
        self.assertEqual(form.parameters, None)
        self.assertEqual(form.status, form.formErrorsMessage)

    def test_raise_action_error(self):
        form = self.get_import_form()

        try:
            form.raise_action_error('testmessage')
        except ActionExecutionError, e:
            self.assertEqual(e.error.message, 'testmessage')
        else:
            assert False, "untriggered exception"
