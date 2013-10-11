
from mock import Mock
from pyramid import testing

from .. import TestCase, mock_query
from tailbone.views import autocomplete


class BareAutocompleteViewTests(TestCase):

    def view(self, **kwargs):
        request = testing.DummyRequest(**kwargs)
        return autocomplete.AutocompleteView(request)

    def test_attributes(self):
        view = self.view()
        self.assertRaises(AttributeError, getattr, view, 'mapped_class')
        self.assertRaises(AttributeError, getattr, view, 'fieldname')

    def test_filter_query(self):
        view = self.view()
        query = Mock()
        filtered = view.filter_query(query)
        self.assertIs(filtered, query)

    def test_make_query(self):
        view = self.view()
        # No mapped_class defined for view.
        self.assertRaises(AttributeError, view.make_query, 'test')

    def test_query(self):
        view = self.view()
        query = Mock()
        view.make_query = Mock(return_value=query)
        filtered = view.query('test')
        self.assertIs(filtered, query)

    def test_display(self):
        view = self.view()
        instance = Mock()
        # No fieldname defined for view.
        self.assertRaises(AttributeError, view.display, instance)

    def test_call(self):
        # Empty or missing query term yields empty list.
        view = self.view(params={})
        self.assertEqual(view(), [])
        view = self.view(params={'term': None})
        self.assertEqual(view(), [])
        view = self.view(params={'term': ''})
        self.assertEqual(view(), [])
        view = self.view(params={'term': '\t'})
        self.assertEqual(view(), [])
        # No mapped_class defined for view.
        view = self.view(params={'term': 'bogus'})
        self.assertRaises(AttributeError, view)


class SampleAutocompleteViewTests(TestCase):

    def setUp(self):
        super(SampleAutocompleteViewTests, self).setUp()
        self.Session_query = autocomplete.Session.query
        self.query = mock_query()
        autocomplete.Session.query = self.query

    def tearDown(self):
        super(SampleAutocompleteViewTests, self).tearDown()
        autocomplete.Session.query = self.Session_query

    def view(self, **kwargs):
        request = testing.DummyRequest(**kwargs)
        view = autocomplete.AutocompleteView(request)
        view.mapped_class = Mock()
        view.fieldname = 'thing'
        return view

    def test_make_query(self):
        view = self.view()
        view.mapped_class.thing.ilike.return_value = 'whatever'
        self.assertIs(view.make_query('test'), self.query)
        view.mapped_class.thing.ilike.assert_called_with('%test%')
        self.query.filter.assert_called_with('whatever')
        self.query.order_by.assert_called_with(view.mapped_class.thing)

    def test_call(self):
        self.query.all.return_value = [
            Mock(uuid='1', thing='first'),
            Mock(uuid='2', thing='second'),
            ]
        view = self.view(params={'term': 'bogus'})
        self.assertEqual(view(), [
                {'label': 'first', 'value': '1'},
                {'label': 'second', 'value': '2'},
                ])
