# vim:fileencoding=utf-8
import re

from strutils import force_unicode

RE_KEYWORD_EXTRACT = re.compile(u'名詞')
RE_KEYWORD_URL = re.compile(r'(http(s)?:\/\/[A-Za-z0-9%&=~?+-_/.#]+)')
RE_KEYWORD_EXTRACT_IGNORE = re.compile(ur'^[()\-!?"#$%&\'\",.;ー]')
RE_KEYWORD_EXTRACT_IGNORE_KANA = re.compile(ur'^[あ-ん０１２３４５６７８９]+$')
RE_NORMALIZE = re.compile(u'[\u30FC\uFF0D\u2015\u2010]')

__all__ = (
    'extract_keywords',
    'optimize',
    'hankaku',
    'normalize',
    'Token',
    'Tokenizer',
)

def extract_keywords(s, cmpfunc=None, dic_encoding='utf-8'):
    """
    キーワード抽出
    """
    import MeCab
    m = MeCab.Tagger("-Ochasen")
    n = m.parseToNode(RE_KEYWORD_URL.sub(',', optimize(s)).encode(dic_encoding))
    d = {}
    w = u''
    score = 0
    while n:
        features = unicode(n.feature, dic_encoding).split(',')
        # 名詞を抽出
        surface = unicode(n.surface, dic_encoding)
        if RE_KEYWORD_EXTRACT.match(features[0]) and not RE_KEYWORD_EXTRACT_IGNORE.match(surface):
            w += surface
            score += 1
        else:
            if w:
                if len(w) >= 2 and not RE_KEYWORD_EXTRACT_IGNORE_KANA.match(w):
                    if not w in d:
                        d[w] = 0
                    d[w] += 1 #score
                w = u''
                score = 0
        n = n.next
    # ソート
    if cmpfunc:
        cmp_keywords = cmpfunc
    else:
        def cmp_keywords(i1, i2):
            if i1[1] == i2[1]:
                # 長さが同じ場合
                try:
                    if s.index(i1[0]) < s.index(i2[0]):
                        return 1
                except:
                    return -1
                return -1
            return cmp(i1[1], i2[1])

    return sorted(d.items(), cmp=cmp_keywords, reverse=True)

def optimize(s):
    """
    全角記号英数字を半角に、半角かなを全角に
    """
    import zenhan
    s = zenhan.z2h(s, zenhan.ASCII)
    return zenhan.h2z(s, zenhan.KANA)

def hankaku(s):
    import zenhan
    s = zenhan.z2h(s, zenhan.ASCII)
    return zenhan.z2h(s, zenhan.KANA)

def normalize(s):
    """
    全角記号英数字を半角に、半角かなを全角に
    全角数字を半角数字に
    全角の[ー－―‐]を - に
    """
    import zenhan
    s = RE_NORMALIZE.sub('-', s)
    s = zenhan.z2h(s, zenhan.ASCII | zenhan.DIGIT)
    return zenhan.h2z(s, zenhan.KANA)

def token_callback_decorator(callback, min_word_length=1, ignore_word_re=None, word_classes=None):
    def token_callback(word, features):
        def _def_callback(word, features):
            return Token.new(word, "utf8", features=features)

        cb = callback or _def_callback

        token_list = cb(word, features)
        if not isinstance(token_list, (list, tuple)):
            token_list = (token_list,)
        for token in token_list:
            if token is not None and len(token) >= min_word_length and \
                    ((ignore_word_re is None) or not ignore_word_re.match(token)) and \
                    ((word_classes is None) or token.features["word_class"] in word_classes):
                yield token
    return token_callback

class Token(unicode):

    @classmethod
    def new(cls, word, encoding="ascii", features={}):
        token = cls(word, encoding)
        token.features = {
            "word_class": None,
            "sub_word_class1": None,
            "sub_word_class2": None,
            "sub_word_class3": None,
            "conjugated": None, 
            "conjugation": None,
            "base": None,
            "reading": None,
            "pronunciation": None,
        }
        token.features.update(features)
        return token

# MeCab feature マッピング
FEATURE_MAP = (
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
class Tokenizer(object):
    """
    日本語を汎用的に分割するトーケンアイザー

    token_callbackは word(単語), と特徴辞書を引数として受け取る関数です。
    
    特徴辞書はトーケンの特徴を名前として定義されている辞書です。
    {
        "word_class": 品詞,
        "sub_word_class1": 品詞細分類1,
        "sub_word_class2": 品詞細分類2,
        "sub_word_class3": 品詞細分類3,
        "conjugated": 活用形, (「サ変・スル」,「特殊・ナイ」など
        "conjugation": 活用型, (未然形、基本形など)
        "base": 原形,
        "reading": 読み,
        "pronunciation": 発音,
    }
            
    >>> t = Tokenizer(min_word_length=2, token
    """

    def __init__(self, encoding="utf8", min_word_length=1, ignore_word_re=None, token_callback=None, word_classes=None):
        self.encoding = encoding
        self.min_word_length = min_word_length
        self.ignore_word_re = ignore_word_re
        
        self.token_callback = token_callback_decorator(token_callback, min_word_length, ignore_word_re, word_classes)

    def tokenize(self, obj):
        import MeCab
        tagger = MeCab.Tagger("-Ochasen")
        n = tagger.parseToNode(force_unicode(obj, encoding=self.encoding).encode("utf8"))
        n = n.next

        while n:
            if n.surface:
                features_dict = {}
                for i, feature in enumerate(map(self._clean_feature, n.feature.split(','))):
                    features_dict[FEATURE_MAP[i]] = feature
                
                # 名詞を抽出
                for token in self.token_callback(n.surface, features_dict):
                    yield token 

            n = n.next

    def _clean_feature(self, feature):
        feature = feature.strip()
        return feature if feature != "*" else None
