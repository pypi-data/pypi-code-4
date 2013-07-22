
import locale

try:
    locale.setlocale(locale.LC_ALL, '')
except:
    pass

# Unit test output goes out stderr.  No worries.

import unittest
from mdx_smartypants.spants import smartyPants as sp
from mdx_smartypants.spants import Quotes

Quotes.reset()

# These are the original smartypants tests. Leaving them here
# in their original, unaltered format for regression purposes.
# New tests will be added in the cleaner py.test format.

class TestSmartypantsAllAttributes(unittest.TestCase):
    # the default attribute is "1", which means "all".

    def test_dates(self):
        self.assertEqual(sp("1440-80's"), "1440-80&#8217;s")
        self.assertEqual(sp("1440-'80s"), "1440-&#8216;80s")
        self.assertEqual(sp("1440---'80s"), "1440&#8211;&#8216;80s")
        self.assertEqual(sp("1960s"), "1960s")  # no effect.
        self.assertEqual(sp("1960's"), "1960&#8217;s")
        self.assertEqual(sp("one two '60s"), "one two &#8216;60s")
        self.assertEqual(sp("'60s"), "&#8216;60s")

    def test_skip_tags(self):
        self.assertEqual(
            sp("""<script type="text/javascript">\n<!--\nvar href = "http://www.google.com";\nvar linktext = "google";\ndocument.write('<a href="' + href + '">' + linktext + "</a>");\n//-->\n</script>"""), 
               """<script type="text/javascript">\n<!--\nvar href = "http://www.google.com";\nvar linktext = "google";\ndocument.write('<a href="' + href + '">' + linktext + "</a>");\n//-->\n</script>""")
        self.assertEqual(
            sp("""<p>He said &quot;Let's write some code.&quot; This code here <code>if True:\n\tprint &quot;Okay&quot;</code> is python code.</p>"""), 
               """<p>He said &#8220;Let&#8217;s write some code.&#8221; This code here <code>if True:\n\tprint &quot;Okay&quot;</code> is python code.</p>""")


    def test_ordinal_numbers(self):
        self.assertEqual(sp("21st century"), "21st century")  # no effect.
        self.assertEqual(sp("3rd"), "3rd")  # no effect.

    def test_educated_quotes(self):
        self.assertEqual(sp('''"Isn't this fun?"'''), '''&#8220;Isn&#8217;t this fun?&#8221;''')

