#!/usr/bin/python
# -*- coding: utf-8 -*-
#   Copyright 2010 Jasper van den Bosch <jasper@ilogue.com>

import unittest
from mock import Mock
from webtest import Submit
from ilogue.readable import assertMethod
from ilogue.readable import assertionMethod


class FormMatcherTestCase(unittest.TestCase):

    def test_Submit_method_fails_if_multiple_forms_match(self):
        from ilogue.readable.formmatcher import FormMatcher
        forms = {'1':self.mockForm(), '2':self.mockForm()}
        matcher = FormMatcher(forms)
        with self.assertRaisesRegex(AssertionError, 'Multiple'):
            matcher.submit()

    def test_Submit_by_default_delegates_to_inner_form_but_can_use_passed_httpApp(self):
        from ilogue.readable.formmatcher import FormMatcher
        form1 = self.mockForm()
        matcher = FormMatcher({'1':form1})
        matcher.submit()
        assertMethod(form1.submit).wasCalled()

    def test_Submit_fails_on_form_not_based_on_WebTest_TestApp(self):
        from ilogue.readable.formmatcher import FormMatcher
        form1 = self.mockForm()
        matcher = FormMatcher({'1':form1}, testappBased=False)
        with self.assertRaises(TypeError):
            matcher.submit()

    def test_Submit_toServerApp_on_form_not_based_on_WebTest_calls_its_post_method(self):
        from ilogue.readable.formmatcher import FormMatcher
        form1 = self.mockFormWithSubmit()
        mockApp = Mock()
        matcher = FormMatcher({'1':form1}, testappBased=False)
        matcher.submit(toServerApp=mockApp)
        (assertMethod(mockApp.post).wasCalled()
            .withArguments(form1.action, dict(form1.submit_fields())))

    def test_Accepts_matcher_for_submit_label(self):
        from ilogue.readable.formmatcher import FormMatcher
        form1 = self.mockFormWithSubmit()
        formMatcher = FormMatcher({'1':form1})
        (assertionMethod(formMatcher.withSubmitButtonLabeled)
            .doesNotFailIfPassedMatchingMatcher()
            .failsWithAppropriateMessageIfPassedNonMatchingMatcher())

    def mockForm(self):
        f = Mock()
        f.text = 'MockedForm'
        return f

    def mockFormWithSubmit(self,disabled=False):
        f = self.mockForm()
        #def __init__(self, form, tag, name, pos, value=None, id=None, **attrs):
        submitField = Submit(None,None,None,None,value = 'xxx')
        f.fields.items.return_value = [('afield',(submitField,))]
        f.submit_fields.return_value = [('field1','value1'),('field2','value2')]
        return f


if __name__ == '__main__':
    unittest.main()
