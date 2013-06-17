# -*- coding: utf-8 -*-
##############################################################################
#
# Copyright (c) 2005 Jim Washington and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""JSON Tests
jwashin 2005-08-18
"""
import unittest

try:
    import simplejson as json
except ImportError:
    import json

ReadException = ValueError

def spaceless(aString):
    return aString.replace(' ','')

class JSONTests(unittest.TestCase):

    def testReadString(self):
        s = u'"hello"'
        self.assertEqual(json.loads(s) ,'hello')

    def testWriteString(self):
        s = 'hello'
        self.assertEqual(json.dumps(s), '"hello"')

    def testEscapes(self):
        s = '"http:\/\/www.example.org"'
        self.assertEqual(json.loads(s), 'http://www.example.org')

    def testReadInt(self):
        s = u"1"
        self.assertEqual(json.loads(s), 1)

    def testReadNegInt(self):
        s = u"-1"
        self.assertEqual(json.loads(s), -1)

    def testReadFloat(self):
        s = '1.334'
        self.assertEqual(json.loads(s), 1.334)

    def testReadEFloat1(self):
        s = u"1.334E2"
        self.assertEqual(json.loads(s), 133.4)

    def testReadEFloat2(self):
        s = u"1.334E-02"
        self.assertEqual(json.loads(s), 0.01334)

    def testReadeFloat1(self):
        s = u"1.334e2"
        self.assertEqual(json.loads(s), 133.4)

    def testReadeFloat2(self):
        s = u"1.334e-02"
        self.assertEqual(json.loads(s), 0.01334)

    def xtestWriteFloat(self):
        s = 1.334
        self.assertEqual(json.dumps(s), "1.334")

    def xtestWriteDecimal(self):
        try:
            from decimal import Decimal
            s = Decimal('1.33')
            self.assertEqual(json.dumps(s), "1.33")
        except ImportError:
            pass

    def xtestReadNegFloat(self):
        s = u"-1.334"
        self.assertAlmostEqual(json.loads(s), -1.334)

    def testWriteNegFloat(self):
        s = -1.334
        self.assertAlmostEqual(float(json.dumps(s)), s)

    def testReadEmptyDict(self):
        s = u"{}"
        self.assertEqual(json.loads(s), {})

    def testWriteEmptyList(self):
        s = []
        self.assertEqual(json.dumps(s), "[]")

    def testWriteEmptyTuple(self):
        s = ()
        self.assertEqual(json.dumps(s), "[]")

    def testReadEmptyList(self):
        s = u"[]"
        self.assertEqual(json.loads(s), [])

    def testWriteEmptyDict(self):
        s = {}
        self.assertEqual(json.dumps(s), '{}')

    def testReadTrue(self):
        s = u"true"
        self.assertEqual(json.loads(s), True)

    def testWriteTrue(self):
        s = True
        self.assertEqual(json.dumps(s), "true")

    def testReadStringTrue(self):
        s = u'"true"'
        self.assertEqual(json.loads(s), 'true')

    def testWriteStringTrue(self):
        s = "True"
        self.assertEqual(json.dumps(s), '"True"')

    def testReadStringNull(self):
        s = u'"null"'
        self.assertEqual(json.loads(s), 'null')

    def testWriteStringNone(self):
        s = "None"
        self.assertEqual(json.dumps(s), '"None"')

    def testReadFalse(self):
        s = u"false"
        self.assertEqual(json.loads(s), False)

    def testWriteFalse(self):
        s = False
        self.assertEqual(json.dumps(s), 'false')

    def testReadNull(self):
        s = u"null"
        self.assertEqual(json.loads(s), None)

    def testWriteNone(self):
        s = None
        self.assertEqual(json.dumps(s), "null")

    def testReadDictOfLists(self):
        s = u'{"a":[],"b":[]}'
        self.assertEqual(json.loads(s), {'a':[],'b':[]})

    def testReadDictOfListsWithSpaces(self):
        s = u'{  "a" :    [],  "b"  : []  }    '
        self.assertEqual(json.loads(s), {'a':[],'b':[]})

    def testWriteDictOfLists(self):
        s = {'a':[],'b':[]}
        self.assertEqual(spaceless(json.dumps(s)), '{"a":[],"b":[]}')

    def testWriteDictOfTuples(self):
        s = {'a':(),'b':()}
        self.assertEqual(spaceless(json.dumps(s)), '{"a":[],"b":[]}')

    def testWriteDictWithNonemptyTuples(self):
        s = {'a':('fred',7),'b':('mary',1.234)}
        w = json.dumps(s)
        self.assertEqual(spaceless(w), '{"a":["fred",7],"b":["mary",1.234]}')

    def testWriteVirtualTuple(self):
        s = 4,4,5,6
        w = json.dumps(s)
        self.assertEqual(spaceless(w), '[4,4,5,6]')

    def testReadListOfDicts(self):
        s = u"[{},{}]"
        self.assertEqual(json.loads(s), [{},{}])

    def testReadListOfDictsWithSpaces(self):
        s = u" [ {    } ,{   \n} ]   "
        self.assertEqual(json.loads(s), [{},{}])

    def testWriteListOfDicts(self):
        s = [{},{}]
        self.assertEqual(spaceless(json.dumps(s)), "[{},{}]")

    def testWriteTupleOfDicts(self):
        s = ({},{})
        self.assertEqual(spaceless(json.dumps(s)), "[{},{}]")

    def testReadListOfStrings(self):
        s = '["a","b","c"]'
        self.assertEqual(json.loads(s), ['a', 'b', 'c'])

    def testReadListOfStringsWithSpaces(self):
        s = ' ["a"    ,"b"  ,\n  "c"]  '
        self.assertEqual(json.loads(s), ['a', 'b', 'c'])

    def testReadStringWithWhiteSpace(self):
        s = ur'"hello \tworld"'
        self.assertEqual(json.loads(s), 'hello \tworld')

    def testWriteMixedList(self):
        o = ['OIL',34,199L,38.5]
        self.assertEqual(spaceless(json.dumps(o)), '["OIL",34,199,38.5]')

    def testWriteMixedTuple(self):
        o = ('OIL',34,199L,38.5)
        self.assertEqual(spaceless(json.dumps(o)), '["OIL",34,199,38.5]')

    def testWriteStringWithWhiteSpace(self):
        s = 'hello \tworld'
        self.assertEqual(json.dumps(s), r'"hello \tworld"')

    def testWriteListofStringsWithApostrophes(self):
        s = ["hasn't","don't","isn't",True,"won't"]
        w = json.dumps(s)
        self.assertEqual(spaceless(w), '["hasn\'t","don\'t","isn\'t",true,"won\'t"]')

    def testWriteTupleofStringsWithApostrophes(self):
        s = ("hasn't","don't","isn't",True,"won't")
        w = json.dumps(s)
        self.assertEqual(spaceless(w), '["hasn\'t","don\'t","isn\'t",true,"won\'t"]')

    def testWriteListofStringsWithRandomQuoting(self):
        s = ["hasn't","do\"n't","isn't",True,"wo\"n't"]
        w = json.dumps(s)
        assert "true" in w

    def testWriteStringWithDoubleQuote(self):
        s = "do\"nt"
        w = json.dumps(s)
        self.assertEqual(w, '"do\\\"nt"')

    def testReadStringWithEscapedSingleQuote(self):
        s = '"don\'t tread on me."'
        self.assertEqual(json.loads(s), "don't tread on me.")

    def testWriteStringWithEscapedDoubleQuote(self):
        s = 'he said, \"hi.'
        t = json.dumps(s)
        self.assertEqual(t, '"he said, \\\"hi."')

    def testReadStringWithEscapedDoubleQuote(self):
        s = r'"She said, \"Hi.\""'
        self.assertEqual(json.loads(s), 'She said, "Hi."')

    def testReadStringWithNewLine(self):
        s = r'"She said, \"Hi,\"\n to which he did not reply."'
        self.assertEqual(json.loads(s), 'She said, "Hi,"\n to which he did not reply.')

    def testReadNewLine(self):
        s = r'"\n"'
        self.assertEqual(json.loads(s), '\n')

    def testWriteNewLine(self):
        s = u'\n'
        self.assertEqual(json.dumps(s), r'"\n"')

    def testWriteSimpleUnicode(self):
        s = u'hello'
        self.assertEqual(json.dumps(s), '"hello"')

    def testReadBackSlashuUnicode(self):
        s = u'"\u0066"'
        self.assertEqual(json.loads(s), 'f')

    def testReadBackSlashuUnicodeInDictKey(self):
        s = u'{"\u0066ather":34}'
        self.assertEqual(json.loads(s), {'father':34})

    def testReadDictKeyWithBackSlash(self):
        s = u'{"mo\\\\use":22}'
        self.assertEqual(json.loads(s), {r'mo\use':22})

    def testWriteDictKeyWithBackSlash(self):
        s = {"mo\\use":22}
        self.assertEqual(json.dumps(s), r'{"mo\\use": 22}')

    def testWriteListOfBackSlashuUnicodeStrings(self):
        s = [u'\u20ac',u'\u20ac',u'\u20ac']
        self.assertEqual(spaceless(json.dumps(s)), u'["\\u20ac","\\u20ac","\\u20ac"]')

    def testWriteEscapedHexCharacter(self):
        s = json.dumps(u'\u1001')
        self.assertEqual(u'"\\u1001"', s)

    def testWriteHexUnicode(self):
        s = unicode('\xff\xfe\xbf\x00Q\x00u\x00\xe9\x00 \x00p\x00a\x00s\x00a\x00?\x00', 'utf-16')
        self.assertEqual(json.dumps(s), '"\\u00bfQu\\u00e9 pasa?"') # '"¿Qué pasa?"'

    def testWriteDosPath(self):
        s = 'c:\\windows\\system'
        self.assertEqual(json.dumps(s), '"c:\\\\windows\\\\system"')

    def testWriteDosPathInList(self):
        s = ['c:\windows\system', 'c:\\windows\\system', r'c:\windows\system']
        self.assertEqual(json.dumps(s), '["c:\\\\windows\\\\system", "c:\\\\windows\\\\system", "c:\\\\windows\\\\system"]')

    def readImportExploit(self):
        s = ur"\u000aimport('os').listdir('.')"
        json.loads(s)

    def testImportExploit(self):
        self.assertRaises(ReadException, self.readImportExploit)

    def readClassExploit(self):
        s = ur'''"__main__".__class__.__subclasses__()'''
        json.loads(s)

    def testReadClassExploit(self):
        self.assertRaises(ReadException, self.readClassExploit)

    def readBadJson(self):
        s = "'DOS'*30"
        json.loads(s)

    def testReadBadJson(self):
        self.assertRaises(ReadException, self.readBadJson)

    def readUBadJson(self):
        s = ur"\u0027DOS\u0027*30"
        json.loads(s)

    def testReadUBadJson(self):
        self.assertRaises(ReadException, self.readUBadJson)

    def testReadEncodedUnicode(self):
        obj = '"La Peña"'
        r = json.loads(obj, encoding='utf-8')
        self.assertEqual(r, unicode('La Peña','utf-8'))

    def testUnicodeFromNonUnicode(self):
        obj = '"\u20ac"'
        r = json.loads(obj)
        self.assertEqual(r, u'\u20ac')

    def testUnicodeInObjectFromNonUnicode(self):
        obj = '''"['\u20ac', '\u20acCESS', 'my\u20ACCESS']"'''
        r = json.loads(obj)
        self.assertEqual(r, u"['\u20ac', '\u20acCESS', 'my\u20acCESS']")

    def testWriteWithEncoding(self):
        obj = u"'La Peña'"
        r = json.dumps(obj.encode('latin-1'), encoding='latin-1')
        self.assertEqual(r, '"\'La Pe\\u00f1a\'"')

    def testWriteWithEncodingBaseCases(self):
        input_uni =  u"Árvíztűrő tükörfúrógép"
        good_result = '"\\u00c1rv\\u00edzt\\u0171r\\u0151 t\\u00fck\\u00f6rf\\u00far\\u00f3g\\u00e9p"'
        #
        # from utf8
        obj = input_uni.encode('utf-8')
        r = json.dumps(obj, encoding='utf-8')
        self.assertEqual(r, good_result)
        #
        # from unicode
        obj = input_uni
        r = json.dumps(obj)
        self.assertEqual(r, good_result)
        #
        # from latin2
        obj = input_uni.encode('latin2')
        r = json.dumps(obj, encoding='latin2')
        self.assertEqual(r, good_result)
        #
        # from unicode, encoding is ignored
        obj = input_uni
        r = json.dumps(obj, encoding='latin2')
        self.assertEqual(r, good_result)
        #
        # same with composite types, uni
        good_composite_result = (
		u'["\\u00c1rv\\u00edzt\\u0171r\\u0151 t\\u00fck\\u00f6rf\\u00far\\u00f3g\\u00e9p", '
		  '"\\u00c1rv\\u00edzt\\u0171r\\u0151 t\\u00fck\\u00f6rf\\u00far\\u00f3g\\u00e9p"]')
        obj = [input_uni, input_uni]
        r = json.dumps(obj)
        self.assertEqual(r, good_composite_result)
        #
        # same with composite types, utf-8
        obj = [input_uni.encode('utf-8'), input_uni.encode('utf-8')]
        r = json.dumps(obj, encoding='utf-8')
        self.assertEqual(r, good_composite_result)
        #
        # same with composite types, latin2
        obj = [input_uni.encode('latin2'), input_uni.encode('latin2')]
        r = json.dumps(obj, encoding='latin2')
        self.assertEqual(r, good_composite_result)
        #
        # same with composite types, mixed utf-8 with unicode
        obj = [input_uni, input_uni.encode('utf-8')]
        r = json.dumps(obj, encoding='utf-8')
        self.assertEqual(r, good_composite_result)
        #
        # XXX The usage of site default encoding

def test_suite():
    loader = unittest.TestLoader()
    return loader.loadTestsFromTestCase(JSONTests)

if __name__=='__main__':
    unittest.TextTestRunner().run(test_suite())
