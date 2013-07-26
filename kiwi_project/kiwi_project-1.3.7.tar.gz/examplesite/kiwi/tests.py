#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from kiwi.utils.treeview import RawTreeMaker, XmlTreeMaker, TemplatedTree

SEQTEST = [
    {'title': u'Accueil', 'id': 1, 'parent': None, 'uri': u'Home'},
    {'title': u'Section 1', 'id': 2, 'parent': None, 'uri': u'Section1'},
    {'title': u'Section 2', 'id': 3, 'parent': None, 'uri': u'Section2'},
    {'title': u'Section 2.1', 'id': 6, 'parent': 3, 'uri': u'Section2-1'},
    {'title': u'Section 2.2', 'id': 7, 'parent': 3, 'uri': u'Section2-2'},
    {'title': u'Section 2.2.1', 'id': 9, 'parent': 7, 'uri': u'Section2-2-1'},
    {'title': u'Section 2.2.2', 'id': 10, 'parent': 7, 'uri': u'Section2-2-2'},
    {'title': u'Section 2.3', 'id': 8, 'parent': 3, 'uri': u'Section2-3'},
    {'title': u'Section 3', 'id': 4, 'parent': None, 'uri': u'Section3'},
    {'title': u'Section 4', 'id': 5, 'parent': None, 'uri': u'Section4'},
    {'title': u'Section 4.1', 'id': 12, 'parent': 5, 'uri': u'Section4-1'},
    {'title': u'Section 4.2', 'id': 13, 'parent': 5, 'uri': u'Section4-2'},
    {'title': u'Section 5', 'id': 11, 'parent': None, 'uri': u'Section5'}
]

RAWFORMAT_TEST_ATTEMPT = """* Accueil
* Section 1
* Section 2
  * Section 2.1
  * Section 2.2
    * Section 2.2.1
    * Section 2.2.2
  * Section 2.3
* Section 3
* Section 4
  * Section 4.1
  * Section 4.2
* Section 5
"""
XMLFORMAT_TEST_ATTEMPT = """<root>
<entry id="1" title="Accueil"/>
<entry id="2" title="Section 1"/>
<entry id="3" title="Section 2">
  <entry id="6" title="Section 2.1"/>
  <entry id="7" title="Section 2.2">
    <entry id="9" title="Section 2.2.1"/>
    <entry id="10" title="Section 2.2.2"/>
</entry>
  <entry id="8" title="Section 2.3"/>
</entry>
<entry id="4" title="Section 3"/>
<entry id="5" title="Section 4">
  <entry id="12" title="Section 4.1"/>
  <entry id="13" title="Section 4.2"/>
</entry>
<entry id="11" title="Section 5"/>
</root>"""
TEMPLATE_TEST_ATTEMPT = """ooo"""
PATHLINE_TEST1_ATTEMPT = """Section 1 (2)"""
PATHLINE_TEST2_ATTEMPT = """Section 2 (3) > Section 2.2 (7) > Section 2.2.2 (10)"""
PATHLINE_TEST3_ATTEMPT = """Section 4 (5)"""
PATHLINE_TEST4_ATTEMPT = """Section 4 (5) > Section 4.1 (12)"""

class TreeviewTestCase(unittest.TestCase):
    """
    Tests unitaires de treeview
    """
    def test_001_RawFormat(self):
        """Test avec RawTreeMaker"""
        treeobject = RawTreeMaker(seq=SEQTEST)
        treeobject.get_tree()
        self.assertEquals(treeobject.render(), RAWFORMAT_TEST_ATTEMPT)

    def test_002_Pathline(self):
        """Test du calcul de pathline"""
        treeobject = RawTreeMaker(seq=SEQTEST)
        treeobject.get_tree()
        TEST1 = " > ".join(["%s (%s)"%(s['title'], s['id']) for s in treeobject.get_pathline(2)])
        TEST2 = " > ".join(["%s (%s)"%(s['title'], s['id']) for s in treeobject.get_pathline(10)])
        TEST3 = " > ".join(["%s (%s)"%(s['title'], s['id']) for s in treeobject.get_pathline(5)])
        TEST4 = " > ".join(["%s (%s)"%(s['title'], s['id']) for s in treeobject.get_pathline(12)])
        self.assertEquals(TEST1, PATHLINE_TEST1_ATTEMPT)
        self.assertEquals(TEST2, PATHLINE_TEST2_ATTEMPT)
        self.assertEquals(TEST3, PATHLINE_TEST3_ATTEMPT)
        self.assertEquals(TEST4, PATHLINE_TEST4_ATTEMPT)

    def test_003_XMLFormat(self):
        """Test avec XmlTreeMaker"""
        treeobject = XmlTreeMaker(seq=SEQTEST)
        treeobject.get_tree()
        self.assertEquals(treeobject.render(), XMLFORMAT_TEST_ATTEMPT)

    #def test_004_Template(self):
        #"""Test avec TemplatedTree"""
        #W2Xobject = Wiki2XhtmlParser()
        #self.assertEquals(treeobject.render(), TEMPLATE_TEST_ATTEMPT)

if __name__ == "__main__":
    unittest.main()
