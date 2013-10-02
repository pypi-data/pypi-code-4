#!/usr/bin/env python

# Name: spellchecker.py
# Author: Philip Zerull
# Date Created: Friday April 13, 2013


import os
import sys
import re
import enchant
from philutils.containers import DotDict


letterkeeper = re.compile(r'[^A-Za-z]+')
excess_space_stripper = re.compile(r'(\s)(\s+)')
spelling_dictionary = enchant.Dict('en_US')


def spellchecker(somestring):
    cleansed_text = somestring.lower()
    cleansed_text = letterkeeper.sub(' ', cleansed_text)
    cleansed_text = excess_space_stripper.sub(r'\1', cleansed_text)
    wordset = dict()
    for word in cleansed_text.split(' '):
        if word in wordset:
            wordset[word].count += 1
        elif len(word):
            is_correct = spelling_dictionary.check(word)
            if is_correct:
                suggestion_list = []
            else:
                suggestion_list = spelling_dictionary.suggest(word)
                for suggestion in suggestion_list:
                    possibility1 = suggestion.replace(' ', '')
                    possibility2 = suggestion.replace('-', '')
                    if word in (possibility1, possibility2):
                        is_correct = True
                        suggestion_list = []
                        break
                wordset[word] = DotDict(
                    count=1,
                    suggestions=suggestion_list,
                    is_correct=is_correct
                )
    return wordset


if __name__ == '__main__':
    filename = sys.argv[1]
    content = open(filename, 'rb').read().decode('utf-8')
    results = spellchecker(content)
    for messup in results:
        print(messup, ': ', results[messup], '\n')
