from unittest import TestCase

from django.template import (
    Template, TemplateSyntaxError,
    Context, VariableDoesNotExist,
)
from pygments.util import ClassNotFound, OptionError


class PygmyTestCase(TestCase):
    """
    Adds `assertIn` support for Python 2.6 since it uses `TestCase` class
    from `unitest` module.
    """
    def assertIn(self, test_value, expected_set):
        msg = "%s did not occur in %s" % (test_value, expected_set)
        self.assert_(test_value in expected_set, msg)


class PygmyTemplateTagTests(PygmyTestCase):
    def render(self, t):
        return Template(t).render(Context())

    def test_pygments_valid_output(self):
        output = self.render("{% load pygmy %}{% pygmy 'import os' %}")
        expected_output = """<div class="highlight"><pre><span class="n">import</span> <span class="n">os</span>\n</pre></div>\n"""

        self.assertEqual(output, expected_output)

    def test_htmlformatter_valid_options(self):
        output = self.render("{% load pygmy %}{% pygmy 'import os' linenos='True' linenostart=9 %}")
        self.assertIn("import", output)
        self.assertIn("9", output)

        output = self.render("{% load pygmy %}{% with 7 as varname %}{% pygmy 'import os' linenos='True' linenostart=varname %}{% endwith %}")
        self.assertIn("import", output)
        self.assertIn("7", output)

        output = self.render("{% load pygmy %}{% with 'import os' as code %}{% pygmy code %}{% endwith %}")
        self.assertIn("import", output)

        output = self.render("{% load pygmy %}{% with code='import random' line=8 %}{% pygmy code linenos='True' linenostart=line lexer='python' %}{% endwith %}")
        self.assertIn("import", output)
        self.assertIn("8", output)

    def test_htmlformatter_invalid_options(self):
        self.assertRaises(LookupError, self.render,
            "{% load pygmy %}{% pygmy 'import os' encoding='<?>' %}")

        self.assertRaises(OptionError, self.render,
            "{% load pygmy %}{% pygmy 'import os' full='!' %}")

    def test_parsing_errors(self):
        "There are various ways that the template tag won't parse codez."

        self.assertRaises(TemplateSyntaxError, self.render,
            "{% load pygmy %}{% pygmy %}")
        self.assertRaises(TemplateSyntaxError, self.render,
            "{% load pygmy %}{% pygmy '' %}")
        self.assertRaises(TemplateSyntaxError, self.render,
            "{% load pygmy %}{% pygmy as '' %}")
        self.assertRaises(VariableDoesNotExist, self.render,
            "{% load pygmy %}{% pygmy [] %}")

    def test_lexer_invalid_name(self):
        self.assertRaises(ClassNotFound, self.render,
            "{% load pygmy %}{% pygmy 'import os' lexer='fake_lexer' %}")

        self.assertRaises(ClassNotFound, self.render,
            "{% load pygmy %}{% pygmy 'import os' lexer='PythonLexer' %}")
