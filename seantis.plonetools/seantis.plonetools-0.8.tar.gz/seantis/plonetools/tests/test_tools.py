# -*- coding: utf-8 -*-

from App.config import getConfiguration, setConfiguration
from plone import api

from zope import i18n
from zope.i18nmessageid import MessageFactory

from Products.ZCatalog.interfaces import ICatalogBrain

from seantis.plonetools import tests
from seantis.plonetools import tools


class TestTools(tests.IntegrationTestCase):

    def test_get_parent(self):

        folder = self.new_temporary_folder(title='parent')
        new_type = self.new_temporary_type()

        with self.user('admin'):
            obj = api.content.create(
                id='test',
                type=new_type.id,
                container=folder
            )

        brain = tools.get_brain_by_object(obj)

        self.assertEqual(tools.get_parent(brain).Title, 'parent')
        self.assertEqual(tools.get_parent(obj).title, 'parent')

        self.assertTrue(ICatalogBrain.providedBy(tools.get_parent(brain)))
        self.assertTrue(isinstance(tools.get_parent(obj), folder.__class__))

    def test_in_debug_mode(self):
        cfg = getConfiguration()

        cfg.debug_mode = False
        setConfiguration(cfg)

        self.assertFalse(tools.in_debug_mode())

        cfg.debug_mode = True
        setConfiguration(cfg)

        self.assertTrue(tools.in_debug_mode())

    def test_is_existing_portal_type(self):
        new_type = self.new_temporary_type()

        self.assertTrue(tools.is_existing_portal_type(new_type.id))
        self.assertFalse(tools.is_existing_portal_type('inexistant'))

    def test_safe_html(self):
        self.assertEqual(
            '<div></div>',
            tools.safe_html('<div><script>alert("x");</script></div>')
        )

    def test_get_type_info_by_behavior(self):
        basic_behavior = 'plone.app.dexterity.behaviors.metadata.IBasic'

        basic_type = self.new_temporary_type(behaviors=[basic_behavior])
        self.new_temporary_type(behaviors=[])

        self.assertEqual(
            tools.get_type_info_by_behavior(basic_behavior), [basic_type]
        )

    def test_get_type_info_by_schema(self):
        model = """<?xml version='1.0' encoding='utf8'?>
        <model xmlns="http://namespaces.plone.org/supermodel/schema">
            <schema>
                <field name="foo" type="zope.schema.TextLine" />
            </schema>
        </model>
        """

        new_type = self.new_temporary_type(model_source=model)
        self.assertEqual(
            tools.get_type_info_by_schema(new_type.lookupSchema()),
            [new_type]
        )

    def test_get_schema_from_portal_type(self):
        new_type = self.new_temporary_type()

        self.assertEqual(
            tools.get_schema_from_portal_type(new_type.id),
            new_type.lookupSchema()
        )

    def test_get_brain_by_object(self):
        with self.user('admin'):
            obj = api.content.create(
                id='test',
                type=self.new_temporary_type().id,
                container=self.new_temporary_folder()
            )

        brain = tools.get_brain_by_object(obj)
        self.assertIs(type(brain.getObject()), type(obj))
        self.assertEqual(brain.id, obj.id)

    def test_invert_dictionary(self):
        input = {
            1: 'x',
            2: 'x',
            3: 'y'
        }
        output = {
            'x': [1, 2],
            'y': [3]
        }
        self.assertEqual(tools.invert_dictionary(input), output)

    def test_add_attribute_to_metadata(self):
        catalog = api.portal.get_tool('portal_catalog')

        tools.add_attribute_to_metadata('test')
        self.assertIn('test', catalog._catalog.schema)

        # ensure that a second call doesn't do anything
        tools.add_attribute_to_metadata('test')
        self.assertIn('test', catalog._catalog.schema)

    def test_order_fields_by_schema(self):

        model = """<?xml version='1.0' encoding='utf8'?>
        <model xmlns="http://namespaces.plone.org/supermodel/schema">
            <schema>
                <field name="first" type="zope.schema.TextLine"></field>
                <field name="second" type="zope.schema.TextLine"></field>
            </schema>
        </model>"""

        schema = self.new_temporary_type(model_source=model).lookupSchema()

        self.assertEqual(
            tools.order_fields_by_schema(
                ['second', 'x', 'last', 'first'], schema
            ),
            ['first', 'second', 'x', 'last']
        )

    def test_translator(self):
        _ = MessageFactory('plone')
        self.assertEqual(
            tools.translator(self.request, domain='plone')(_(u'Comment')),
            i18n.translate(_(u'Comment'), target_language='en', domain='plone')
        )

    def test_unicode_collate_sortkey(self):
        self.assertEqual(
            sorted(u'AaÄäÖöOo', key=tools.unicode_collate_sortkey()),
            list(u'aAäÄoOöÖ')
        )
