# -*- coding: utf-8 -*-
import argparse
import polib
import re
import time
import urllib2

from translate import Translator


DEFAULT = re.compile(r'Default:\s(.*)')
SOURCE_LANGUAGE = 'en'
BREATHE = 0.25


def log(bash_color, type, text):
    print u'[\033[{0}m {1} \033[0m] {2}'.format(bash_color, type, text)


def autotranslate(path, target_language, ignore_already_translated=True):
    """Given a po file which is opened using polib and processed through
       Google Translator for all untranslated items by default
    """

    try:
        catalog = polib.pofile(path)
    except UnicodeDecodeError:
        raise Exception(("Encoding problem while parsing {0}, are you "
                         "sure that's a PO file?").format(path))

    translator = Translator(to_lang=target_language, from_lang=SOURCE_LANGUAGE)
    try:
        for idx, entry in enumerate(catalog):

            if ignore_already_translated and entry.translated():
                continue

            default_text = DEFAULT.match(entry.comment)
            if default_text:
                to_translate = default_text.group(1)
            else:
                to_translate = entry.msgid

            try:
                translated = translator.translate(to_translate)
            except urllib2.HTTPError as e:
                log(31, 'Error', u'{0:s} raised {1}: {2:s}'.format(
                    entry, e.__class__, e))
                continue

            log(32, 'Success', u'{0} -> {1}'.format(to_translate, translated))

            # Save entry
            catalog[idx].msgstr = translated
            time.sleep(BREATHE)

    except KeyboardInterrupt:
        log(31, 'Quit', '')

    catalog.save()


def AutoTranslator():
    parser = argparse.ArgumentParser(description='Translate Po files.')
    parser.add_argument('-i', dest='input', action='append', nargs=2,
                              required=True, metavar=('<locale>', '<po file>'),
                              help='Locale and filename of po-file to process')
    parser.add_argument('-u', dest='update', action='store_const',
                              default=False, const=True,
                              help='Force updating translations by '
                                   'retranslating all msgids.')
    options = parser.parse_args()

    for locale, pofile in options.input:
        autotranslate(pofile, locale, not options.update)
