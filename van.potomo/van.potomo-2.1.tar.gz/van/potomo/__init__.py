##############################################################################
#
# Copyright (c) 2009 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
import os

from distutils.command.build import build as build_
from setuptools.command.develop import develop as develop_
from distutils.core import Command
from pythongettext.msgfmt import Msgfmt

class build(build_):

    sub_commands = build_.sub_commands[:]
    sub_commands.append(('van_build_i18n', None))


class develop(develop_):

    def install_for_development(self):
        # we have to run egg_info before ourselves to make sure
        # SOURCES.txt exists and is up to date
        self.run_command("egg_info")
        ei = self.get_finalized_command("egg_info")
        sources = os.path.join(ei.egg_info, 'SOURCES.txt')
        sources = open(sources, 'r').read().splitlines()
        _compile_pofiles([s for s in sources if _is_pofile(s)])
        return develop_.install_for_development(self)


class van_build_i18n(Command):

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        build_py = self.get_finalized_command("build_py")
        sources = []
        for package, src_dir, build_dir, filenames in build_py.data_files:
            for filename in filenames:
                filename = os.path.join(build_dir, filename)
                if _is_pofile(filename):
                    sources.append(filename)
        _compile_pofiles(sources)

def _is_pofile(filename):
    if filename.endswith('.po') and os.path.exists(filename):
        # file may not exist if it has recently been deleted and
        # is still in SOURCES.txt
        return True
    return False

def _compile_pofiles(files):
    for src in files:
        dest = '%smo' % src[:-2]
        if not os.path.exists(dest):
            _compile(src, dest)
        else:
            src_mtime = os.stat(src)[8]
            dest_mtime = os.stat(dest)[8]
            if src_mtime > dest_mtime:
                _compile(src, dest)

def _compile(src, dest):
    print ('Compiling %s to %s' % (src, dest))
    f = open(dest, 'wb')
    try:
        f.write(Msgfmt(src).get())
    finally:
        f.close()
