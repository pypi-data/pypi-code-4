from plone import api

from seantis.people.interfaces import IPerson

from seantis.people.supermodel import set_detail_fields
from seantis.people import tests


class TestList(tests.IntegrationTestCase):

    def test_person_view_positions(self):
        with self.user('admin'):
            person_type = self.new_temporary_type(behaviors=[
                IPerson.__identifier__
            ])
            person = api.content.create(
                id='test',
                type=person_type.id,
                container=self.new_temporary_folder(),
                name='test',
                town='test',
                empty=''
            )
            schema = person_type.lookupSchema()
            view = person.unrestrictedTraverse('@@view')

        set_detail_fields(schema, {'top': ['name'], 'left': ['empty']})

        # empty positions are not visible and are therefore left out completely
        self.assertEqual(view.visible_positions(), ['top'])

        # split screen is available only if left and right are available
        self.assertFalse(view.split_screen())

        set_detail_fields(schema, {'left': ['name'], 'right': ['town']})

        self.assertEqual(view.visible_positions(), ['left', 'right'])
        self.assertTrue(view.split_screen())
