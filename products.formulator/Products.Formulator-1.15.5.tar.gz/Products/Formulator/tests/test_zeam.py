# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Formulator.testing import FunctionalLayer, TestRequest
from Products.Formulator.zeamsupport import IFormulatorField, IFormulatorWidget
from zeam.form.base import Fields, Widgets, FormData, DISPLAY
from zope.interface.verify import verifyObject


class IntegrationTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.layer.login('manager')
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Formulator']
        factory.manage_add('form', 'Test Form')
        form = self.root.form
        form.manage_addField(
            'text_field', 'Name', 'StringField',
            required=True, default='Arthur van Bossnia')
        form.manage_addField(
            'age_field', 'Age', 'IntegerField',
            required=False)
        form.manage_addField(
            'life_field', 'Life', 'TextAreaField')
        form.manage_addField(
            'deceased_field', 'Deceased ?', 'CheckBoxField')

    def test_fields(self):
        """Create fields.
        """
        fields = Fields(self.root.form)
        self.assertEqual(len(fields), 4)
        # String
        text_field = fields.get('text_field')
        self.assertTrue(verifyObject(IFormulatorField, text_field))
        self.assertEqual(text_field.meta_type, 'StringField')
        self.assertEqual(text_field.identifier, 'text_field')
        self.assertEqual(text_field.title, 'Name')
        self.assertEqual(text_field.readonly, False)
        self.assertEqual(text_field.required, True)
        self.assertEqual(text_field.getDefaultValue(None), 'Arthur van Bossnia')

        # Checkbox
        checkbox_field = fields.get('deceased_field')
        self.assertTrue(verifyObject(IFormulatorField, checkbox_field))
        self.assertEqual(checkbox_field.meta_type, 'CheckBoxField')
        self.assertEqual(checkbox_field.identifier, 'deceased_field')
        self.assertEqual(checkbox_field.title, 'Deceased ?')
        self.assertEqual(checkbox_field.readonly, False)
        self.assertEqual(checkbox_field.required, False)
        self.assertEqual(checkbox_field.getDefaultValue(None), False)

    def test_display_widgets(self):
        """Create widgets to input data with Formulator fields.
        """
        form = FormData(self.root, TestRequest())
        form.mode = DISPLAY
        widgets = Widgets(form=form)
        widgets.extend(Fields(self.root.form))
        self.assertEqual(len(widgets), 4)

        # String
        text_widget = widgets.get('field-text-field')
        self.assertTrue(verifyObject(IFormulatorWidget, text_widget))

        # Checkbox
        checkbox_widget = widgets.get('field-deceased-field')
        self.assertTrue(verifyObject(IFormulatorWidget, checkbox_widget))

        # Update
        widgets.update()

        # Render
        self.assertEqual(text_widget.render(), u'Arthur van Bossnia')
        self.assertEqual(checkbox_widget.render(), u'No')

    def test_input_widgets(self):
        """Create widgets to input data with Formulator fields.
        """
        form = FormData(self.root, TestRequest())
        widgets = Widgets(form=form)
        widgets.extend(Fields(self.root.form))
        self.assertEqual(len(widgets), 4)

        # String
        text_widget = widgets.get('field-text-field')
        self.assertTrue(verifyObject(IFormulatorWidget, text_widget))
        self.assertEqual(text_widget.identifier, 'field-text-field')
        self.assertEqual(text_widget.title, 'Name')
        self.assertEqual(text_widget.description, '')
        self.assertEqual(text_widget.required, True)

        # Checkbox
        checkbox_widget = widgets.get('field-deceased-field')
        self.assertTrue(verifyObject(IFormulatorWidget, checkbox_widget))
        self.assertEqual(checkbox_widget.identifier, 'field-deceased-field')
        self.assertEqual(checkbox_widget.title, 'Deceased ?')
        self.assertEqual(checkbox_widget.description, '')
        self.assertEqual(checkbox_widget.required, False)

        # Update
        widgets.update()

        # Render
        self.assertEqual(
            text_widget.render(),
            u'<div class="field field-required"><input class="field field-required" id="field-text-field" name="field_text_field" size="20" type="text" value="Arthur van Bossnia" /></div> <input type="hidden" value="1" name="marker_field_text_field" />')
        self.assertEqual(
            checkbox_widget.render(),
            u'<input class="field" id="field-deceased-field" name="field_deceased_field" type="checkbox" /> <input type="hidden" value="1" name="marker_field_deceased_field" />')

def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(IntegrationTestCase))
    return suite
