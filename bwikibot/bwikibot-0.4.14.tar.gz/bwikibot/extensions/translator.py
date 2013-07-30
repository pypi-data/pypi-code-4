import argparse
from pprint import pprint
import sys

from bwikibot.api import Wiki
from bwikibot import lexer
from bwikibot.cli import action

parser = argparse.ArgumentParser(
    description='Get some text and print another'
)

parser.add_argument(
    '-f', dest='from_lang', default="en",
    help='language to translate from'
)
parser.add_argument(
    '-t', dest='to_lang', default="uk",
    help='language to translate to'
)

@action('translate')
def main(*argv):
    ''' Automate translation of wikitext from one language to another
        -f from_lang (for example 'en')
        -t to lang (for example 'uk')
    '''
    args = parser.parse_args(argv)

    translator = Translator(args.from_lang, args.to_lang)
    for line in sys.stdin:
        if line.strip():
            print(translator.translate(line[:-1]))
        else:
            print()

class Translator:
    redirects_to_follow = 5
    def __init__(self, from_lang, to_lang,
        logger=lambda msg: print(msg, file=sys.stderr)
    ):
        self.wiki = Wiki('http://%s.wikipedia.org/w/api.php' % from_lang)
        self.to_lang = to_lang
        self.logger = logger

    def translate(self, text):
        tokens = lexer.tokenize(text)
        res = []
        for token in tokens:
            if token[0] == lexer.LINK:
                self.logger('Translating "%s"' % token[1])
                trans = self._translate_segment(token[1])
                self.logger('Transled as "%s"' % trans)
                full = token[1] == token[2] and ':' in token[1]
                token = token[0], trans, trans if full else token[2]
            res.append(lexer.token_text(token))
        return ''.join(res)

    def _translate_segment(self, text):
        res = self._save_case(text, self._traslate_page_name(text))
        return res

    @staticmethod
    def _save_case(text, translation):
        if text[0].islower():
            return translation[0].lower() + translation[1:]
        else:
            return translation

    def _traslate_page_name(self, name):
        page = self.wiki.page(name)
        for i in range(self.redirects_to_follow):
            redirect = page.redirect()
            if not redirect:
                break
            else:
                page = redirect
        return page.interwikis().get(self.to_lang, name)
