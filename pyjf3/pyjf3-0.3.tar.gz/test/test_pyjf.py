# -*- coding: ShiftJIS -*-
import unittest, random, io

from pyjf3 import *

try:
    unicode
except NameError:
    unicode = str

class TestGuess(unittest.TestCase):
    def testEmpty(self):
        self.failUnlessEqual(guess(b''), ASCII)

    def testSJIS(self):
        s = io.open("sjis.txt", "rb").read()
        self.failUnlessEqual(guess(s), SJIS)

    def testEUC(self):
        s = io.open("euc.txt", "rb").read()
        self.failUnlessEqual(guess(s), EUC)

    def testJIS(self):
        s = io.open("jis.txt", "rb").read()
        self.failUnlessEqual(guess(s), JIS)

    def testUTF8(self):
        s = io.open("utf8.txt", "rb").read()
        self.failUnlessEqual(guess(s), UTF8)

    def testSingleKana(self):
        sjis = b'\xb1\xb2\xb3\xb4\xb5'
        euc = b'\x8e\xb1\x8e\xb2\x8e\xb3\x8e\xb4\x8e\xb5'
        jis = b'\x1b(I12345\x1b(B'
        utf8 = b'\xef\xbd\xb1\xef\xbd\xb2\xef\xbd\xb3\xef\xbd\xb4\xef\xbd\xb5'
        
        self.failUnlessEqual(guess(sjis), SJIS)
        self.failUnlessEqual(guess(euc), EUC)
        self.failUnlessEqual(guess(jis), JIS)
        self.failUnlessEqual(guess(utf8), UTF8)
        
        sjis = b'\xb1\xb2\xb3\xb4\xb5\x83A\x83C\x83E\x83G\x83I'
        euc = b'\x8e\xb1\x8e\xb2\x8e\xb3\x8e\xb4\x8e\xb5\xa5\xa2\xa5\xa4\xa5\xa6\xa5\xa8\xa5\xaa'
        jis = b'\x1b(I12345\x1b(B\x1b$B%"%$%&%(%*\x1b(B'
        utf8 = b'\xef\xbd\xb1\xef\xbd\xb2\xef\xbd\xb3\xef\xbd\xb4\xef\xbd\xb5\xe3\x82\xa2\xe3\x82\xa4\xe3\x82\xa6\xe3\x82\xa8\xe3\x82\xaa'
        
        self.failUnlessEqual(guess(sjis), SJIS)
        self.failUnlessEqual(guess(euc), EUC)
        self.failUnlessEqual(guess(jis), JIS)
        self.failUnlessEqual(guess(utf8), UTF8)
        

class TestEncodigs(unittest.TestCase):
    def _conv(self, sjis):
        euc = sjistoeuc(sjis)
        jis = sjistojis(sjis)

        u = unicode(sjis, "cp932")
        self.failUnlessEqual(u, unicode(euctosjis(euc), "cp932"))
        self.failUnlessEqual(u, unicode(jistosjis(jis), "cp932"))
        self.failUnlessEqual(jis, euctojis(euc))
        self.failUnlessEqual(euc, jistoeuc(jis))

    def testConv(self):
        sjis = io.open("sjis.txt", "rb").read()
        self._conv(sjis)
    
    def testSingleKaka(self):
        sjis = b'\xb1\xb2\xb3\xb4\xb5\x83A\x83C\x83E\x83G\x83I'
        self._conv(sjis)
        sjis = io.open("hankana.txt", "rb").read()
        self._conv(sjis)

    def testGaiji(self):
        sjis = b'\xf0\x40'
        euc = sjistoeuc(sjis)
        self.failUnlessEqual(euc.decode('euc-jp'), u"〓")

    def testNECKanji(self):
        sjis = io.open("nec.txt", "rb").read()
        self._conv(sjis)
        
        sjis = io.open("necibm.txt", "rb").read()
        self._conv(sjis)
        
    def testIBMKanji(self):
        sjis = io.open("ibm.txt", "rb").read()

        euc = sjistoeuc(sjis)
        jis = sjistojis(sjis)
        self._conv(sjis)

    def testRandom(self):
        s = b"".join([
            io.open("sjis.txt", "rb").read(),
            io.open("hankana.txt", "rb").read(),
            io.open("nec.txt", "rb").read(),
            io.open("necibm.txt", "rb").read(),
            io.open("ibm.txt", "rb").read(),
        ])
        u = list(unicode(s, "cp932"))
        random.shuffle(u)
        u = u"".join(u)

        sjis = u.encode("cp932")
        self._conv(sjis)

class TestConv(unittest.TestCase):
    def testKana(self):
        s = unicode(io.open("hankana.txt", "rb").read(), "cp932")
        full = kanatofull(s)
        half = kanatohalf(full)

        self.failUnlessEqual(s, half)
        
    def testConv(self):
        half = u"abcdefgABCDEFG0123456789+*`[]\\"
        full = u'\uff41\uff42\uff43\uff44\uff45\uff46\uff47' \
               u'\uff21\uff22\uff23\uff24\uff25\uff26\uff27' \
               u'\uff10\uff11\uff12\uff13\uff14\uff15\uff16' \
               u'\uff17\uff18\uff19\uff0b\uff0a\uff40\uff3b' \
               u'\uff3d\uffe5'

        self.failUnlessEqual(tofull(half), full)
        self.failUnlessEqual(half, tohalf(full))
        
    def testRandom(self):
        s = unicode(b"".join([
                    io.open("sjis.txt", "rb").read(),
                    io.open("hankana.txt", "rb").read(),
                    io.open("nec.txt", "rb").read(),
                    io.open("necibm.txt", "rb").read(),
                    io.open("ibm.txt", "rb").read()]),
                "cp932")
        
        u = list(s)
        random.shuffle(u)
        s = u"".join(u)

        full = tofull(s)
        half = tohalf(full)
        
        self.failUnlessEqual(half, tohalf(s))

class TestNengo(unittest.TestCase):
    def testNengo(self):
        self.failUnlessEqual(getnengo(1989, 1, 8), (u'\u5e73\u6210', 1))
        self.failUnlessEqual(getnengo(1989, 1, 7), (u'\u662d\u548c', 64))
        self.failUnlessEqual(getnengo(1926, 12, 25, True), (u'S', 1))
        self.failUnlessEqual(getnengo(1926, 12, 24, True), (u'T', 15))

    def testYear(self):
        self.failUnlessEqual(heiseitoyear(1), 1989)
        self.failUnlessEqual(showatoyear(1), 1926)
        self.failUnlessEqual(taishotoyear(1), 1912)
        self.failUnlessEqual(meijitoyear(1), 1868)


class TestWrap(unittest.TestCase):
    def testSimple(self):
        s = u"abcd   defg   ghi    jl\n abc def ghi jlk"
        lines = []
        for line in wrap(s, 3):
            lines.append(line)

        expected = [u'abc', u'd  ', u' ', u'def', u'g  ', u' ', 
            u'ghi', u'   ', u' jl', u' ', u'abc', u' ', u'def', 
            u' ', u'ghi', u' ', u'jlk']
            
        self.failUnlessEqual(expected, lines)

    def testKana(self):
        s = u"あいうえおかきくけこ"
        lines1 = []
        for line in wrap(s, 1):
            lines1.append(line)
        lines2 = []
        for line in wrap(s, 2):
            lines2.append(line)
        lines3 = []
        for line in wrap(s, 3):
            lines3.append(line)
        lines4 = []
        for line in wrap(s, 4):
            lines4.append(line)
        
        expected1 = [u"あ", u"い", u"う", u"え", u"お", u"か", u"き", u"く", u"け", u"こ"]
        self.failUnlessEqual(expected1, lines1)
        self.failUnlessEqual(expected1, lines2)
        self.failUnlessEqual(expected1, lines3)
        expected4 = [u"あい", u"うえ", u"おか", u"きく", u"けこ"]
        self.failUnlessEqual(expected4, lines4)

    def testMix(self):
        s = u"abcあdefいghiうjklえmnoおpqrかstuきくけabcdこ"
        lines1 = []
        for line in wrap(s, 1):
            lines1.append(line)

        self.failUnlessEqual(list(s), lines1)

        lines4 = []
        for line in wrap(s, 4):
            lines4.append(line)

        expected = [
            u"abc", u"あ", u"def", u"い", u"ghi", u"う", 
            u"jkl", u"え", u"mno", u"お", u"pqr", u"か", 
            u"stu", u"きく", u"け", u"abcd", u"こ"]
        
        self.failUnlessEqual(expected, lines4)

        lines6 = []
        for line in wrap(s, 6):
            lines6.append(line)

        expected = [u"abcあ", u"defい", u"ghiう", u"jklえ",
            u"mnoお", u"pqrか", u"stuき", u"くけ",u"abcdこ"]
            
        self.failUnlessEqual(expected, lines6)

    def testKinsoku(self):
        s = u"あいう。えおか。きくけこさし、"
        lines = []
        for line in wrap(s, 6):
            lines.append(line)

        expected = [u"あい", u"う。え", u"おか。", u"きくけ",
            u"こさ", u"し、"]
            
        self.failUnlessEqual(expected, lines)

if __name__ == '__main__':
    unittest.main()


