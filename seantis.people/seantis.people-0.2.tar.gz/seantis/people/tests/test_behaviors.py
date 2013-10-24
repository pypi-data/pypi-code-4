from plone import api

from seantis.people.supermodel import set_title_fields
from seantis.people import (
    behaviors,
    interfaces,
    tests
)


class TestBehavior(tests.IntegrationTestCase):

    def is_behavior_assignable(self, behavior, interface, factory):

        # use a throwaway type with the given behavior
        new_type = self.new_temporary_type(behaviors=[behavior])

        # create an object of said type
        with self.user('admin'):
            obj = api.content.create(
                id=new_type.id,
                type=new_type.id,
                container=self.new_temporary_folder()
            )

        # adapt the behavior's interface
        adapted = interface(obj)

        # ensure that an instance of the factory is the result
        self.assertIs(type(adapted), factory)
        self.assertIs(adapted.context, obj)

    def test_person_behavior_assignable(self):
        self.is_behavior_assignable(
            interfaces.IPerson.__identifier__,
            interfaces.IPerson,
            behaviors.Person
        )

    def test_person_title_no_influence_if_not_activated(self):
        blank_type = self.new_temporary_type()
        set_title_fields(blank_type.lookupSchema(), ['foo', 'bar'])
        
        with self.user('admin'):
            blank_obj = api.content.create(
                id='',
                type=blank_type.id,
                container=self.new_temporary_folder(),
                foo='stop',
                bar='hammertime!'
            )

        self.assertEqual(blank_obj.title, '')

    def test_person_title_behavior(self):
        new_type = self.new_temporary_type(
            behaviors=[
                interfaces.INameFromPerson.__identifier__
            ]
        )

        set_title_fields(new_type.lookupSchema(), ['foo', 'bar'])

        with self.user('admin'):           
            obj = api.content.create(
                id='',
                type=new_type.id,
                container=self.new_temporary_folder(),
                foo='stop',
                bar='hammertime!'
            )

        self.assertEqual(obj.title, 'stop hammertime!')
        self.assertEqual(obj.id, 'stop-hammertime')
