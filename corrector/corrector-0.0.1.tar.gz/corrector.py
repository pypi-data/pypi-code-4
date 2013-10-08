#!/usr/bin/env python
#coding=utf-8

import re
from collections import defaultdict

__version__ = '0.0.1'
__author__ = 'solos'
__doc__ = 'A spelling corrector.'


class Corrector():

    def __init__(self, trainfile):

        self.nwords = defaultdict(lambda: 1)
        self.wordmap = defaultdict(dict)
        try:
            content = file(trainfile).read().decode('utf8')
            self.train(self.words(content))
        except Exception, e:
            print e

    def words(self, text):
        return re.findall(r'\S+', text)

    def train(self, words):
        for word in words:
            for i in xrange(0, len(word)-1):
                try:
                    self.wordmap[word[i]].add(word[i+1])
                except:
                    self.wordmap[word[i]] = set([])
                    self.wordmap[word[i]].add(word[i+1])
            self.nwords[word] += 1
        return self.nwords, self.wordmap

    def edits1(self, word):
        n = len(word)
        return set([word[0:i] + word[i+1:] for i in xrange(n)] +  # deletion
                   [word[0:i] + word[i+1] + word[i] + word[i+2:]
                   for i in xrange(n-1)] +  # transposition
                   [word[0:i] + c + word[i+1:] for i in xrange(n)
                   for c in self.wordmap[word[i-1]]] +  # alteration
                   [word[0:i] + c + word[i:] for i in xrange(1, n+1)
                   for c in self.wordmap[word[i-1]]])  # insertion

    def known_edits2(self, word):
        return set(e2 for e1 in self.edits1(word) for e2 in self.edits1(e1)
                   if e2 in self.nwords)

    def known(self, words):
        return set(w for w in words if w in self.nwords)

    def correct(self, word):
        candidates = self.known([word]) or self.known(self.edits1(word)) \
            or self.known_edits2(word) or [word]
        return max(candidates, key=lambda w: self.nwords[w])
