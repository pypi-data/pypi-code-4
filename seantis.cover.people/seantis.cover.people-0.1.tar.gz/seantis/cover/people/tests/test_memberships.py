import json

from uuid import uuid4 as new_uuid
from plone import api
from plone.uuid.interfaces import IUUID

from seantis.people.interfaces import IPerson
from seantis.cover.people import tests


class TestMemberships(tests.IntegrationTestCase):

    def add_layout_row(self, cover):
        layout = cover.cover_layout and json.loads(cover.cover_layout) or []
        id = new_uuid().hex

        layout.append(
            {"type": "row", "children": [{
                "data": {"layout-type": "column", "column-size": 16}, 
                "type": "group", "children": [{
                    "tile-type": "seantis.cover.people.memberlist", 
                    "type": "tile", "id": id
                }], 
                "roles": ["Manager"]
            }]}
        )

        cover.cover_layout = json.dumps(layout)

        cover.reindexObject()

        return 'seantis.cover.people.memberlist/{}'.format(id)

    def test_membership_cleanup(self):

        with self.user('admin'):
            person_type = self.new_temporary_type(
                behaviors=[IPerson.__identifier__]
            )

            cover = api.content.create(
                id='cover',
                type='collective.cover.content',
                container=self.new_temporary_folder()
            )

            person = api.content.create(
                title='person',
                type=person_type.id,
                container=self.new_temporary_folder()
            )

            path = self.add_layout_row(cover)

        tile = cover.restrictedTraverse(path)
        tile.populate_with_object(person)
        
        tile.set_role(IUUID(person), u'test')
        self.assertEqual(tile.get_role(IUUID(person)), u'test')

        tile.remove_item(IUUID(person))
        self.assertEqual(tile.get_role(IUUID(person)), u'')

    def test_memberships_by_cover(self):

        with self.user('admin'):
            person_type = self.new_temporary_type(
                behaviors=[IPerson.__identifier__]
            )

            cover = api.content.create(
                id='cover',
                type='collective.cover.content',
                container=self.new_temporary_folder()
            )

            person = api.content.create(
                title='person',
                type=person_type.id,
                container=self.new_temporary_folder()
            )

            path1 = self.add_layout_row(cover)
            path2 = self.add_layout_row(cover)

        tile1 = cover.restrictedTraverse(path1)
        tile2 = cover.restrictedTraverse(path2)
        
        tile1.populate_with_object(person)
        memberships = IPerson(person).memberships()

        self.assertEqual(tile1.results(), [person])

        self.assertEqual(len(memberships.keys()), 1)
        self.assertEqual(len(memberships.values()[0]), 1)

        # A cover may have multiple entries for a person, but they will
        # only show up as one membership. I thought of supporting the other
        # case, but I feel like multiple memberships (with start/end date and
        # all that stuff) should be reserved for another module. The cover
        # way of using seantis.people should stay simple and dumb.
        tile2.populate_with_object(person)
        memberships = IPerson(person).memberships()

        self.assertEqual(tile1.results(), [person])
        self.assertEqual(tile2.results(), [person])
        self.assertEqual(len(memberships.keys()), 1)
        self.assertEqual(len(memberships.values()[0]), 1)
