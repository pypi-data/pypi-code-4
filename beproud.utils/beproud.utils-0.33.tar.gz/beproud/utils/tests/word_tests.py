#:coding=utf8:

# vim:fileencoding=utf-8
from unittest import TestCase

from beproud.utils.word import * 

TEST_FEATURE_MAP = (
    "word_class",
    "sub_word_class1",
    "sub_word_class2",
    "sub_word_class3",
    "conjugated",
    "conjugation",
    "base",
    "reading",
    "pronunciation",
)

class TokenizerTestCase(TestCase):
    
    def test_encoding(self):
        tokenizer = Tokenizer(encoding="cp932")
        tokens = tokenizer.tokenize(u"これはテスト文章です".encode("cp932"))
        self.assertEqual(len(list(tokens)), 5)

    def test_features(self):
        tokenizer = Tokenizer()
        tokens = tokenizer.tokenize(u"これはテスト文章です")
        for token in tokens:
            for feature in TEST_FEATURE_MAP:
                self.assertTrue(feature in token.features)

    def test_word_classes(self):
        tokenizer = Tokenizer(word_classes=["名詞"])
        tokens = tokenizer.tokenize(u"これはテスト文章です")
        token_list = list(tokens)
        self.assertEquals(len(token_list), 3)
        self.assertEquals(token_list[0], u"これ")
        self.assertEquals(token_list[1], u"テスト")
        self.assertEquals(token_list[2], u"文章")

    def test_min_word_length(self):
        tokenizer = Tokenizer(min_word_length=3)
        tokens = tokenizer.tokenize(u"これはテスト文章です")
        token_list = list(tokens)
        self.assertEquals(len(token_list), 1)
        self.assertEquals(token_list[0], u"テスト")

    def test_callback(self):
        def cb(word, features):
            self.assertTrue(isinstance(features, dict))
            self.assertTrue(isinstance(word, str))
            utf = unicode(word, "utf8") # unicode test
            cb.count += 1
            return Token.new(word, "utf8", features=features)
        cb.count = 0

        tokenizer = Tokenizer(token_callback=cb)
        tokens = tokenizer.tokenize(u"これはテスト文章です")
        self.assertEquals(len(list(tokens)), 5)
        self.assertEquals(cb.count, 5)
    
    def test_callback_none(self):
        def cb(word, features):
            pass
        tokenizer = Tokenizer(token_callback=cb)
        tokens = tokenizer.tokenize(u"これはテスト文章です")
        self.assertEquals(len(list(tokens)), 0)
