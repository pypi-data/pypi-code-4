#coding=utf-8
from __future__ import unicode_literals

import re
import os

from bwikibot.cli import get_wiki, action
from bwikibot.ui import print_diff, ask_y_n
from bwikibot.utils import ON_2

if ON_2:
    from codecs import open


@action('spell')
def spell(*page_name):
    ''' Make autocorrection with dictionary '''
    wiki = get_wiki()

    page = wiki.page(' '.join(page_name))
    text = page.read()
    if not page.exists():
        print('Page "%s" not exists!' % page.title)
        return
    correction = correct(text)

    if correction == text:
        print('Текст в порядку')
        return

    print_diff(text, correction)
    if ask_y_n('Здійснити виправлення?'):
        print('Виправляємо')
        page.write(correction, 'автовиправлення по словнику')


def here(filename):
    return os.path.join(os.path.dirname(__file__), filename)

class Corrector:
    def __init__(self):
        self.substitutions = []

        with open(here('genitive_a_u.txt'), encoding='utf-8') as f:
            self.load_genitive_a_u(f)

    def load_genitive_a_u(self, f):
        for word in f:
            word = word.strip()
            if word.endswith('а'):
                err_end = 'у'
            elif word.endswith('у'):
                err_end = 'а'
            else:
                print('Слово "%s" має помилкове закінчення' % word)
                continue

            self.substitutions.append((
                word[:-1] + err_end + r'\b',
                word
            ))

            word = word.capitalize()
            self.substitutions.append((
                word[:-1] + err_end + r'\b',
                word
            ))

    def correct(self, text):
        for subst in self.substitutions:
            text = re.sub(subst[0], subst[1], text, flags=re.U)
        return text

    __call__ = correct # shortcut for main action of this class

correct = Corrector()
