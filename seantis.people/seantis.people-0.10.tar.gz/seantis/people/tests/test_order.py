from plone import api

from seantis.people.supermodel import (
    set_order
)
from seantis.plonetools import tools

from seantis.people.interfaces import IPerson
from seantis.people import tests


class TestOrder(tests.IntegrationTestCase):

    def test_order(self):
        new_type = self.new_temporary_type(behaviors=[IPerson.__identifier__])
        set_order(new_type.lookupSchema(), ['bar', 'foo'])

        with self.user('admin'):
            obj = api.content.create(
                id='123',
                type=new_type.id,
                container=self.new_temporary_folder(),
                foo='stop',
                bar='hammertime!'
            )

        brain = tools.get_brain_by_object(obj)
        catalog = api.portal.get_tool('portal_catalog')

        self.assertEqual(
            catalog.getIndexDataForRID(brain.getRID())['sortable_title'],
            tools.unicode_collate_sortkey()('hammertime! stop')
        )
