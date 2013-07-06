#####################################################################
# zopyx.authoring
# (C) 2011, ZOPYX Limited, D-72070 Tuebingen. All rights reserved
#####################################################################

import os
import unittest2
from .. import s5

HTML = """
<div id="main-content">
....
<h1>slide 1(orig)</h1>
blabla 1
<h2>slide 1</h2>
text slide 1

<h1>slide 2(orig)</h1>
blabla 2
<h2>slide 2</h2>
text slide 2

<h1>slide 3(orig)</h1>
blabla 3
<h2>slide 3</h2>
text slide 3

</div>
"""

class S5Tests(unittest2.TestCase):

    def testSplitHTMLIntoSlides(self):
        slides = s5.splitHTMLIntoSlides(HTML)
        self.assertEqual(len(slides), 3)
        self.assertTrue('<h1>slide 1</h1>' in slides[0])
        self.assertTrue('<h1>slide 2</h1>' in slides[1])
        self.assertTrue('<h1>slide 3</h1>' in slides[2])

    def testSplitHTMLIntoSlidesOneHugeLine(self):
        return True
        slides = s5.splitHTMLIntoSlides(HTML.replace('\n', ''))
        self.assertEqual(len(slides), 3)
        self.assertTrue('<h1>slide 1</h1>' in slides[0])
        self.assertTrue('<h1>slide 2</h1>' in slides[1])
        self.assertTrue('<h1>slide 3</h1>' in slides[2])

def test_suite():
    from unittest import TestSuite, makeSuite
    suite = TestSuite()
    suite.addTest(makeSuite(S5Tests))
    return suite

