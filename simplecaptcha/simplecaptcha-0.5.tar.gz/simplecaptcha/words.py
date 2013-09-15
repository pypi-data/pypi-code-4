""" Captcha.Words

Utilities for managing word lists and finding random words

SimpleCaptcha Package
Forked from PyCAPTCHA Copyright (C) 2004 Micah Dowty <micah@navi.cx>
"""
import random
import os
from simplecaptcha import file


class WordList(object):
    """A class representing a word list read from disk lazily.  Blank lines and
    comment lines starting with '#' are ignored.  Any number of words per line
    may be used. The list can optionally ingore words not within a given length
    range.  """

    def __init__(self, filename, min_length=None, max_length=None):
        self.words = None
        self.filename = filename
        self.min_length = min_length
        self.max_length = max_length

    def read(self):
        """Read words from disk"""
        f = open(os.path.join(file.data_dir, "words", self.filename), 'rt')

        self.words = []
        for line in f.readlines():
            line = line.strip()
            if not line:
                continue
            if line[0] == '#':
                continue
            for word in line.split():
                if self.min_length is not None and len(word) < self.min_length:
                    continue
                if self.max_length is not None and len(word) > self.max_length:
                    continue
                self.words.append(word)

    def pick(self):
        """Pick a random word from the list, reading it in if necessary"""
        if self.words is None:
            self.read()
        return random.choice(self.words)


# Define several shared word lists that are read from disk on demand
basic_english = WordList("basic-english")
basic_english_restricted = WordList("basic-english", min_length=5, max_length=8)

default_word_list = basic_english_restricted
