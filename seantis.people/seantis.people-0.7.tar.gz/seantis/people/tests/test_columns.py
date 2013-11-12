from plone import api

from seantis.people.supermodel import (
    get_columns,
    set_columns
)
from seantis.plonetools import tools

from seantis.people.supermodel.indexing import on_type_modified
from seantis.people.interfaces import IPerson
from seantis.people import tests


class TestColumns(tests.IntegrationTestCase):

    def test_add_person_column_first(self):
        new_type = self.new_temporary_type(behaviors=[IPerson.__identifier__])

        set_columns(new_type.lookupSchema(), [['foo']])
        on_type_modified(new_type)

        with self.user('admin'):
            obj = api.content.create(
                id='123',
                type=new_type.id,
                container=self.new_temporary_folder(),
                foo='stop',
                bar='hammertime!'
            )

        brain = tools.get_brain_by_object(obj)

        self.assertTrue(hasattr(brain, 'foo'))
        self.assertFalse(hasattr(brain, 'bar'))

        self.assertEqual(brain.foo, 'stop')

    def test_add_person_column_later(self):
        new_type = self.new_temporary_type(behaviors=[IPerson.__identifier__])

        self.assertEqual(get_columns(new_type.lookupSchema()), [])

        with self.user('admin'):
            obj = api.content.create(
                id='123',
                type=new_type.id,
                container=self.new_temporary_folder(),
                foo='stop',
                bar='hammertime!'
            )

        # define the metadata after the obj has been created
        set_columns(new_type.lookupSchema(), [['foo']])

        # which leaves the attribute in a missing value state
        brain = tools.get_brain_by_object(obj)
        self.assertFalse(hasattr(brain, 'foo'))

        # until reindexing happens
        on_type_modified(new_type)
        brain = tools.get_brain_by_object(obj)
        self.assertEqual(brain.foo, 'stop')

    def test_reindex_on_change(self):
        new_type = self.new_temporary_type(behaviors=[IPerson.__identifier__])

        set_columns(new_type.lookupSchema(), [['foo']])
        on_type_modified(new_type)

        with self.user('admin'):
            obj = api.content.create(
                id='123',
                type=new_type.id,
                container=self.new_temporary_folder(),
                foo='stop',
                bar='hammertime!'
            )

        brain = tools.get_brain_by_object(obj)

        self.assertTrue(hasattr(brain, 'foo'))
        self.assertFalse(hasattr(brain, 'bar'))

        self.assertEqual(brain.foo, 'stop')

        set_columns(new_type.lookupSchema(), [['bar']])

        # usually the dexterity fti modified event does this
        on_type_modified(new_type)

        brain = tools.get_brain_by_object(obj)

        # The metadata is not deleted at this point because it is impossible
        # to tell if the metadata is used elsewhere. It's a rather big caveat..
        self.assertTrue(hasattr(brain, 'foo'))
        self.assertTrue(hasattr(brain, 'bar'))

        self.assertEqual(brain.bar, 'hammertime!')
