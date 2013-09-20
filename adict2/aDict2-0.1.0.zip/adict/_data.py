# aDict — simple dictionary handling
#
# Authors:
#     arseniiv <arseniiv@gmail.com>
#
# To the extent possible under law, the author(s) have dedicated all copyright and related and neighboring rights to this software to the public domain worldwide. This software is distributed without any warranty.
# You should have received a copy of the CC0 Public Domain Dedication along with this software. If not, see <http://creativecommons.org/publicdomain/zero/1.0/>.

"""_data.py — aDict data classes
"""

__all__ = [
    'Dictionary',
    'Article',
    'LinkContent',
    'FormContent',
    'Definition'
    ]

from functools import total_ordering as _total_ordering

class Dictionary:
    """aDict dictionary."""
    
    def __init__(self):
        self.properties = {}
        self.articles = []
    
    def _accept_visitor(self, v):
        for k, e in sorted(self.properties.items()):
            v.visit_property(k, e)
        self.articles.sort()
        for e in self.articles:
            e._accept_visitor(v)
    

@_total_ordering
class Article:
    """aDict article."""
    
    def __init__(self, title=None):
        self.title = title # (word, number=0)
        self.transcriptions = []
        self.classes = [] # sw
        self.forms = [] # (sw, text)
        self.etymologies = []
        self.content = None # LinkContent | FormContent | [Definition]
    
    def __eq__(self, other):
        """x.__eq__(y) <==> x==y"""
        word1, num1 = self._title()
        word2, num2 = other._title()
        return word1 == word2 and num1 == num2
    
    def __lt__(self, other):
        """x.__lt__(y) <==> x<y"""
        word1, num1 = self._title()
        word2, num2 = other._title()
        if word1 < word2:
            return True
        elif word1 > word2:
            return False
        else:
            return num1 < num2
    
    def _title(self):
        t = self.title
        if isinstance(t, tuple):
            return t
        elif isinstance(t, str):
            return t, 0
        else:
            return '', 0
    
    def _accept_visitor(self, v):
        v.visit_articleStart(self)
        v.visit_title(self.title)
        for e in self.classes:
            v.visit_class(e)
        for e in self.forms:
            v.visit_form(e)
        for e in self.transcriptions:
            v.visit_transcription(e)
        for e in self.etymologies:
            v.visit_etymology(e)
        if self.content != None:
            if isinstance(self.content, list):
                for e in self.content:
                    e._accept_visitor(v)
            else:
                self.content._accept_visitor(v)
        v.visit_article_end(self)


class LinkContent:
    """aDict article content as link to another article."""
    
    def __init__(self, title=None):
        self.title = title # (word, number)
    
    def _accept_visitor(self, v):
        v.visit_link_content(self.title)


class FormContent:
    """aDict article content as form of another article’s title."""
    
    def __init__(self, form=None):
        self.form = form # (form=None, (word, number))
    
    def _accept_visitor(self, v):
        v.visit_form_content(self.form)


class Definition:
    """aDict article content as a definition of title."""
    
    def __init__(self, meaning=None):
        self.meaning = meaning
        self.examples = [] # (text, text)
        self.idioms = [] # (text, text)
        self.links = [] # (type=None, (word, number))
    
    def _accept_visitor(self, v):
        v.visit_definition_start(self)
        v.visit_meaning(self.meaning)
        for e in self.examples:
            v.visit_example(e)
        for e in self.idioms:
            v.visit_idiom(e)
        for e in self.links:
            v.visit_link(e)
        v.visit_definition_end(self)


# Values in Article.ertmologies, Definition.meaning, .examples, .idioms
# can be strings or (FORMAT_x, str) tuple lists indicating formatted text
FORMAT_NONE = 0  # plain text,                       in source: "abc"
FORMAT_SW = 1    # special word (class, form etc.),  in source: "#abc#"
FORMAT_REM = 2   # parenthesized italicized remark,  in source: "((abc))"
FORMAT_EM = 3    # italicized text,                  in source: "''abc''"

