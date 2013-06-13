from django.template import Template, Context, TemplateSyntaxError
from django.test import TestCase
from pygments.util import ClassNotFound, OptionError


class PygmyTemplateTagTests(TestCase):
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
            "{% load pygmy %}{% pygmy [] %}")
        self.assertRaises(TemplateSyntaxError, self.render,
            "{% load pygmy %}{% pygmy as %}")
        self.assertRaises(TemplateSyntaxError, self.render,
            "{% load pygmy %}{% pygmy '' %}")
        self.assertRaises(TemplateSyntaxError, self.render,
            "{% load pygmy %}{% pygmy as '' %}")
        self.assertRaises(TemplateSyntaxError, self.render,
            "{% load pygmy %}{% pygmy qwerty %}")

    def test_lexer_invalid_name(self):
        self.assertRaises(ClassNotFound, self.render,
            "{% load pygmy %}{% pygmy 'import os' lexer='fake_lexer' %}")
