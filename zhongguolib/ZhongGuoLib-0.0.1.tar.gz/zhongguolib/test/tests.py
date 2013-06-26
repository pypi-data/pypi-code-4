# -*- coding: utf8 -*-
from unittest.case import TestCase
from zhongguolib.constants import *
from zhongguolib.utils import *

class UtilsTestCase(TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_syllabize_numbered_pinyin(self):
        self.assertEqual(syllabize_numbered_pinyin('bao4se3fu2'), u'bàosěfú')

    def test_syllabize_pinyin(self):
        self.assertEqual(syllabize_pinyin('bao4se3fu2'), u'bàosěfú')
        self.assertEqual(syllabize_pinyin(u'bai3du4wen2ku4zi1liao4shi4bai3du4wei2wang3you3ti2gong1de5xin4xi1cun2chu3kong1'),
                        u'bǎidùwénkùzīliàoshìbǎidùwéiwǎngyǒutígōngdexìnxīcúnchǔkōng')

        self.assertEqual(syllabize_pinyin(u'bǎidùwen2ku4zi1liao4shi4bai3du4wei2wang3you3ti2gong1de5xìnxīcun2chu3kong1'),
                          u'bǎidùwénkùzīliàoshìbǎidùwéiwǎngyǒutígōngdexìnxīcúnchǔkōng')

    def test_tone_final(self):
        for char in FINALS_TONES.keys():
            for tone in CHINESE_TONES:
                self.assertEqual(tone_final(char, tone), FINALS_TONES[char][tone])

    def test_detone_final(self):
        for detoned_final, toned_finals in FINALS_TONES.iteritems():
            for toned_final in toned_finals:
                self.assertEqual(detone_final(toned_final), detoned_final)
                
    def test_tone_detone_syllable(self):
        self.assertEqual('bao', detone_syllable(tone_syllable('bao', 1)))
        self.assertEqual('bao', detone_syllable(tone_syllable('bao', 2)))
        self.assertEqual('bao', detone_syllable(tone_syllable('bao', 3)))
        self.assertEqual('bao', detone_syllable(tone_syllable('bao', 4)))

    def test_tone_detone_final(self):
        self.assertEqual('ao', detone_final(tone_final('ao', 1)))
        self.assertEqual('ao', detone_final(tone_final('ao', 2)))
        self.assertEqual('ao', detone_final(tone_final('ao', 3)))
        self.assertEqual('ao', detone_final(tone_final('ao', 4)))

    def test_inifinal(self):
        for initial in SYLLABLES.keys():
            for idx, syllable in enumerate(SYLLABLES[initial]):
                self.assertEqual(inifinal(SYLLABLES[initial][idx]), (initial, syllable.lstrip(initial)))

    def test_validate_syllable(self):
        for initial in SYLLABLES.keys():
            for idx, syllable in enumerate(SYLLABLES[initial]):
                for tone in CHINESE_TONES:
                    self.assertTrue(validate_syllable(tone_syllable(SYLLABLES[initial][idx], tone)))

    def test_tone_syllable(self):
        self.assertEqual(tone_syllable('bao', 4), u'bào')
        self.assertEqual(tone_syllable('se', 2), u'sé')
        self.assertEqual(tone_syllable('fu', 1), u'fū')

    def test_detone_syllable(self):
        self.assertEqual(detone_syllable('bào'), u'bao')
        self.assertEqual(detone_syllable('sé'), u'se')
        self.assertEqual(detone_syllable('fū'), u'fu')

    def test_normalize_syllable(self):
        self.assertEqual(normalize_syllable('bao4'), u'bào')
        self.assertEqual(normalize_syllable('se2'), u'sé')
        self.assertEqual(normalize_syllable('fu1'), u'fū')
        
    def test_decouple_syllables(self):
        self.assertEqual(decouple_syllables('benyouzzaoeu'), ['ben', 'you'])
        self.assertEqual(decouple_syllables('be'), ['be'])
        self.assertEqual(decouple_syllables('a'), ['a'])
