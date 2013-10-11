
from mock import Mock

from .. import TestCase
from tailbone.forms import simpleform


class FormRendererTests(TestCase):

    def test_field_div(self):
        form = Mock()
        form.errors_for = Mock(return_value=[])
        renderer = simpleform.FormRenderer(form)
        renderer.field_div('test', '<p>test</p>')

    def test_field_div_with_errors(self):
        form = Mock()
        form.errors_for = Mock(return_value=["Bogus testing error."])
        renderer = simpleform.FormRenderer(form)
        renderer.field_div('test', '<p>test</p>')

    def test_referrer_field(self):
        form = Mock()
        renderer = simpleform.FormRenderer(form)
        renderer.referrer_field()
