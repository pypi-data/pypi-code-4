# vim:fileencoding=utf-8
from unittest import TestCase

from beproud.utils.strutils import *

class StringUtilsTestCase(TestCase):
    
    def test_trim(self):
        self.assertEqual(trim(u" テスト "), u"テスト")
        self.assertEqual(trim(u"テスト "), u"テスト")
        self.assertEqual(trim(u" テスト"), u"テスト")
        self.assertEqual(trim(u"　テスト　"), u"テスト")
        self.assertEqual(trim(u"テスト　"), u"テスト")
        self.assertEqual(trim(u"　テスト"), u"テスト")
        self.assertEqual(trim(u"　テスト "), u"テスト")

    def test_trim_none(self):
        self.assertEqual(trim(None), 'None')

    def test_force_int(self):
        self.assertEqual(force_int(192), 192)
        self.assertEqual(force_int("192"), 192)
        self.assertEqual(force_int("abc"), None)
        self.assertEqual(force_int("abc", "def"), "def")

    def test_force_int_none(self):
        self.assertEqual(force_int(None, 1), 1)

    def test_force_unicode(self):
        class UnicodeTest(StrAndUnicode):
            def __unicode__(self):
                return u"Unicodeテスト"
        self.assertEqual(force_unicode(UnicodeTest()), u"Unicodeテスト")
        self.assertEqual(force_unicode(22), u"22")
        self.assertEqual(force_unicode(22, strings_only=True), 22)

        self.assertEqual(force_unicode(u"テスト".encode("cp932"), encoding="cp932"), u"テスト") 
    
    def test_make_random_key(self):
        self.assertEqual(len(make_random_key(8)), 8)
        self.assertEqual(len(make_random_key(291)), 291)
        self.assertEqual(len(make_random_key(1)), 1)
    
    def test_make_random_key_empty(self):
        self.assertEqual(make_random_key(0), "")
        self.assertEqual(make_random_key(-1), "")

    def test_abbrev(self):
        self.assertEqual(abbrev('spamspamspam', 6), 'spa...')
        self.assertEqual(abbrev('spamspamspam', 12), 'spamspamspam')
        self.assertEqual(abbrev('eggseggseggs', 11, '....'), 'eggsegg....')
        self.assertEqual(abbrev('eggseggseggs', 1), 'e')
        self.assertEqual(abbrev('eggseggseggs', 2, '.'), 'e.')

    def test_abbrev_unicode(self):
        self.assertEqual(abbrev(u'テストテストテスト', 6), u'テスト...')
        self.assertEqual(abbrev(u'テストテストテスト', 9), u'テストテストテスト')
        self.assertEqual(abbrev(u'テストテストテスト', 8, '....'), u'テストテ....')
        self.assertEqual(abbrev(u'テストテストテスト', 1), u'テ')
        self.assertEqual(abbrev(u'テストテストテスト', 2, '.'), u'テ.')
