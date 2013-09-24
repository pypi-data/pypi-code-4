import unittest
from mock import Mock
from ilogue.readable import assertionMethod, assertMethod, setupMethod
from ilogue.readable.matching import that

#form().withSubmitButtonLabeled('file.name')

class FormMatcher2TestCase(unittest.TestCase):


    def test_withSubmitButtonLabeled(self):
        from ilogue.readable import FormMatcher
        form = FormMatcher().withSubmitButtonLabeled('target SubmitLabel')
        nobutton = '<form></form>'
        buttonotherlabel = '<form><input type="submit" value="other label"></submit></form>'
        expected = '<form><input type="submit" value="target SubmitLabel"></submit></form>'
        self.assertFalse(form.matches(nobutton))
        self.assertFalse(form.matches(buttonotherlabel))
        self.assertTrue(form.matches(expected),
            'Should match, but didnt, with msg: '+str(form.matchFor(expected)))
        
