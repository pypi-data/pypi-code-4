#!/usr/bin/python
# -*- coding: utf-8 -*-
import os
import path_mngt

APP_DIR = path_mngt.get_share_dir()
_ = None
def set_lang_wrapper():
    import sys
    import locale
    import gettext
    #  The translation files will be under
    #  @LOCALE_DIR@/@LANGUAGE@/LC_MESSAGES/@APP_NAME@.mo
    APP_NAME = path_mngt.appli_name
    # .mo files will then be located in APP_Dir/i18n/LANGUAGECODE/LC_MESSAGES/
    LOCALE_DIR = os.path.join(APP_DIR, 'i18n')

    # Now we need to choose the language. We will provide a list, and gettext
    # will use the first translation available in the list
    #
    #  (on desktop is usually LANGUAGES)
    DEFAULT_LANGUAGES = os.environ.get('LANG', '').split(':')
    DEFAULT_LANGUAGES += ['en_US']

    lc, encoding = locale.getdefaultlocale()
    if lc:
      languages = [lc]

    # Concat all languages (env + default locale),
    #  and here we have the languages and location of the translations
    languages += DEFAULT_LANGUAGES
    mo_location = LOCALE_DIR

    # Lets tell those details to gettext
    gettext.install(True, localedir=None)
    gettext.bind_textdomain_codeset(APP_NAME, "UTF-8")
    language = gettext.translation(APP_NAME, mo_location,
        languages=languages, fallback=True)
    global _
    _ =  language.gettext
    if sys.version_info.major == 2:
        _ =  language.lgettext

def identity(s):
    return s
_ = identity
if os.path.exists(APP_DIR):
    set_lang_wrapper()

