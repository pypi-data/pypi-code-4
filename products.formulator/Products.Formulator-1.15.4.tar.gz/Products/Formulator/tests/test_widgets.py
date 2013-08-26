# -*- coding: utf-8 -*-
# Copyright (c) 2013  Infrae. All rights reserved.
# See also LICENSE.txt

import unittest

from Products.Formulator.testing import FunctionalLayer


class WidgetTestCase(unittest.TestCase):
    layer = FunctionalLayer

    def setUp(self):
        self.layer.login('manager')
        self.root = self.layer.get_application()
        factory = self.root.manage_addProduct['Formulator']
        factory.manage_add('form', 'Test Form')

    def test_integer(self):
        """Test render an integer value.
        """
        self.root.form.manage_addField('age_field', 'Age', 'IntegerField')
        self.assertEqual(
            self.root.form.age_field.render(value=42),
            u'<div><input id="field-age-field" name="field_age_field" size="20" type="text" value="42" /></div>')
        self.assertEqual(
            self.root.form.age_field.render_view(value=42),
            u'42')

    def test_string_empty(self):
        """Create a regular TextField and render an empty value.
        """
        self.root.form.manage_addField('text_field', 'Name', 'StringField')
        self.assertEqual(
            self.root.form.text_field.render(value=None),
            u'<div><input id="field-text-field" name="field_text_field" size="20" type="text" value="" /></div>')
        self.assertEqual(
            self.root.form.text_field.render_view(value=None),
            u'')

    def test_string_escape_html(self):
        """Create a regular TextField and render an unicode value
        containing HTML entities.
        """
        self.root.form.manage_addField('text_field', 'Name', 'StringField')
        self.assertEqual(
            self.root.form.text_field.render(value=u"<élèves />"),
            u'<div><input id="field-text-field" name="field_text_field" size="20" type="text" value="&lt;élèves /&gt;" /></div>')
        self.assertEqual(
            self.root.form.text_field.render_view(value=u"<élèves />"),
            u'&lt;élèves /&gt;')

    def test_string_unicode(self):
        """Create a regular TextField and render an unicode value.
        """
        self.root.form.manage_addField('text_field', 'Name', 'StringField')
        self.assertEqual(
            self.root.form.text_field.render(value=u"élèves du primaire"),
            u'<div><input id="field-text-field" name="field_text_field" size="20" type="text" value="élèves du primaire" /></div>')
        self.assertEqual(
            self.root.form.text_field.render_view(value=u"élèves du primaire"),
            u'élèves du primaire')

    def test_textarea_escape_html(self):
        """Create a regular TextAreaField and render an unicode value
        containing HTML entities.
        """
        self.root.form.manage_addField('life_field', 'Life', 'TextAreaField')
        self.assertEqual(
            self.root.form.life_field.render(value=u"<b>élèves</b>"),
            u'<div><textarea cols="40" id="field-life-field" name="field_life_field" rows="5">&lt;b&gt;élèves&lt;/b&gt;</textarea></div>')
        self.assertEqual(
            self.root.form.life_field.render_view(value=u"<b>élèves</b>"),
            u'&lt;b&gt;élèves&lt;/b&gt;')


def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(WidgetTestCase))
    return suite
