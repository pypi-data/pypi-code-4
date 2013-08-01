#!/usr/bin/python
# -*- coding: utf-8 -*-

# Copyright (c) 2013 Eric F <efigue> Figerson
# Author(s):
#   Eric F <eric.foss@free.fr>

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

import os
import facct.path_mngt as path_mngt

_ = lambda x:x
def set_lang_wrapper():
    share_dir = path_mngt.get_share_dir()
    if not os.path.exists(share_dir):
        return

    import sys
    import locale
    import gettext
    #  The translation files (.mo) will be under
    #  @share_dir@/@LANGUAGE@/LC_MESSAGES/@APP_NAME@.mo

    # Now we need to choose the language. We will provide a list, and gettext
    # will use the first translation available in the list
    #
    #  (on desktop is usually LANGUAGES)
    DEFAULT_LANGUAGES = os.environ.get('LANG', '').split(':')
    DEFAULT_LANGUAGES += ['en_US']

    languages = []
    lc, encoding = locale.getdefaultlocale()
    if lc:
      languages = [lc]

    # Concat all languages (env + default locale),
    #  and here we have the languages and location of the translations
    languages += DEFAULT_LANGUAGES

    # Lets tell those details to gettext
    gettext.install(True, localedir=None)
    gettext.bind_textdomain_codeset(path_mngt.appli_name, "UTF-8")
    language = gettext.translation(path_mngt.appli_name, share_dir,
        languages=languages, fallback=True)

    global _
    _ =  language.gettext
    if sys.version_info.major == 2:
        _ =  language.lgettext

set_lang_wrapper()

