from plone import api

from seantis.people import tests
from seantis.people.interfaces import IPerson
from seantis.people.supermodel import set_selectable_fields

from seantis.people.supermodel.indexing import update_related_indexes


class TestIndex(tests.IntegrationTestCase):

    selectable_xml = """<?xml version='1.0' encoding='utf8'?>
        <model  xmlns="http://namespaces.plone.org/supermodel/schema"
                xmlns:people="http://namespaces.plone.org/supermodel/people">
            <schema>
                <people:columns>
                    <people:column selectable="true">
                        <people:item>first</people:item>
                    </people:column>
                    <people:column selectable="true">
                        <people:item>second</people:item>
                    </people:column>
                    <people:column selectable="true">
                        <people:item>third</people:item>
                    </people:column>

                </people:columns>
            </schema>
        </model>"""

    def test_selectable_fields_index(self):
        new_type = self.new_temporary_type(
            behaviors=[IPerson.__identifier__],
            model_source=self.selectable_xml
        )
        schema = new_type.lookupSchema()

        catalog = api.portal.get_tool('portal_catalog')

        ix = '{}_selectable_{}'

        self.assertIn(ix.format(new_type.id, 'first'), catalog.indexes())
        self.assertIn(ix.format(new_type.id, 'second'), catalog.indexes())
        self.assertIn(ix.format(new_type.id, 'third'), catalog.indexes())

        # nothing changes implicitly
        set_selectable_fields(schema, ['third'])

        self.assertIn(ix.format(new_type.id, 'first'), catalog.indexes())
        self.assertIn(ix.format(new_type.id, 'second'), catalog.indexes())
        self.assertIn(ix.format(new_type.id, 'third'), catalog.indexes())

        # the index must be rebuilt by hand (using the web-interface events
        # will take care of that)
        update_related_indexes(new_type)

        self.assertNotIn(ix.format(new_type.id, 'first'), catalog.indexes())
        self.assertNotIn(ix.format(new_type.id, 'second'), catalog.indexes())
        self.assertIn(ix.format(new_type.id, 'third'), catalog.indexes())
