
from mock import Mock
from pyramid import testing

from .. import TestCase, mock_query
from tailbone.views import departments


class DepartmentsGridTests(TestCase):

    def view(self, **kwargs):
        request = testing.DummyRequest(**kwargs)
        return departments.DepartmentsGrid(request)

    def test_filter_map(self):
        view = self.view()
        view.make_filter_map = Mock(return_value='gotcha')
        self.assertEqual(view.filter_map(), 'gotcha')
        view.make_filter_map.assert_called_with(ilike=['name'])

    def test_filter_config(self):
        view = self.view()
        view.make_filter_config = Mock(return_value='yep')
        self.assertEqual(view.filter_config(), 'yep')
        view.make_filter_config.assert_called_with(
            include_filter_name=True, filter_type_name='lk')

    def test_sort_map(self):
        view = self.view()
        view.make_sort_map = Mock(return_value='really')
        self.assertEqual(view.sort_map(), 'really')
        view.make_sort_map.assert_called_with('number', 'name')

    def test_grid_allowed(self):
        view = self.view()
        view.request.has_perm = Mock(return_value=True)
        view.make_grid = Mock()
        g = view.grid()
        self.assertTrue(g.viewable)
        self.assertEqual(g.view_route_name, 'department.read')
        self.assertTrue(g.editable)
        self.assertEqual(g.edit_route_name, 'department.update')
        self.assertTrue(g.deletable)
        self.assertEqual(g.delete_route_name, 'department.delete')

    def test_grid_restricted(self):
        view = self.view()
        view.request.has_perm = Mock(return_value=False)
        grid = Mock(
            viewable=False, view_route_name=None,
            editable=False, edit_route_name=None,
            deletable=False, delete_route_name=None)
        view.make_grid = Mock(return_value=grid)
        g = view.grid()
        self.assertFalse(g.viewable)
        self.assertEqual(g.view_route_name, None)
        self.assertFalse(g.editable)
        self.assertEqual(g.edit_route_name, None)
        self.assertFalse(g.deletable)
        self.assertEqual(g.delete_route_name, None)


class DepartmentCrudTests(TestCase):

    def view(self, **kwargs):
        request = testing.DummyRequest(**kwargs)
        return departments.DepartmentCrud(request)

    def test_fieldset(self):
        view = self.view()
        fieldset = Mock()
        view.make_fieldset = Mock(return_value=fieldset)
        fs = view.fieldset(Mock())
        self.assertIs(fs, fieldset)


class DepartmentsByVendorGridTests(TestCase):

    def view(self, **kwargs):
        request = testing.DummyRequest(**kwargs)
        return departments.DepartmentsByVendorGrid(request)

    def test_query(self):
        query = mock_query()
        view = self.view(params={'uuid': '1'})
        view.make_query = Mock(return_value=query)
        self.assertIs(view.query(), query)

    def test_grid(self):
        view = self.view()
        grid = Mock()
        view.make_grid = Mock(return_value=grid)
        self.assertIs(view.grid(), grid)
