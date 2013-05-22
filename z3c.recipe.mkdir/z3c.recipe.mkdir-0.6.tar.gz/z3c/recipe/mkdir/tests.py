##############################################################################
#
# Copyright (c) 2008 Zope Foundation and Contributors.
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
from __future__ import print_function
import grp
import os
import pwd
import re
import stat
import unittest
import doctest

import zc.buildout.testing
from zope.testing import renormalizing

user = pwd.getpwuid(os.geteuid()).pw_name
group = grp.getgrgid(os.getegid()).gr_name

def dir_entry(path):
    # create a dir entry for file/dir in path.
    def perm(mode):
        # turn file stat mode into rwx...-string
        result = ''
        for grp in oct(mode)[-3:]:
            perms = int(grp)
            for num, sign in ((0o4, 'r'), (0o2, 'w'), (0o1, 'x')):
                result += perms & num and sign or '-'
        return result
    st = os.stat(path)
    type_flag = stat.S_ISDIR(st.st_mode) and 'd' or '-'
    permissions = type_flag + perm(st.st_mode)
    return '%s %s %s %s' % (permissions, user, group, path)

def ls_parts(dir='parts', *subs):
    # list files and directories in `path` with permissions and type.
    # *don't* print 'buildout' as a part
    if subs:
        dir = os.path.join(dir, *subs)
    names = os.listdir(dir)
    names.sort()
    for name in names:
        if name == 'buildout':
            continue
        if os.path.isdir(os.path.join(dir, name)):
            printx('d  ')
        elif os.path.islink(os.path.join(dir, name)):
            printx('l  ')
        else:
            printx('-  ')
        print(name)

def lls(path):
    # list files and directories in `path` with permissions and type.
    for name in sorted(os.listdir(path)):
        print(dir_entry(os.path.join(path, name)))


def printx(*args, **kw):
    import sys
    sys.stdout.write(' '.join(args))

def setUp(test):
    zc.buildout.testing.buildoutSetUp(test)
    zc.buildout.testing.install_develop('z3c.recipe.mkdir', test)
    test.globs['lls'] = lls
    test.globs['ls_parts'] = ls_parts
    test.globs['user'] = user
    test.globs['group'] = group
    test.globs['printx'] = printx
    test.globs['printy'] = print


checker = renormalizing.RENormalizing([
    zc.buildout.testing.normalize_path,
    (re.compile(
        "Couldn't find index page for '[a-zA-Z0-9.]+' "
        "\(maybe misspelled\?\)"
        "\n"),
     ''),
    (re.compile("""['"][^\n"']+z3c.recipe.i18n[^\n"']*['"],"""),
     "'/z3c.recipe.i18n',"),
    (re.compile('#![^\n]+\n'), ''),
    (re.compile('-\S+-py\d[.]\d(-\S+)?.egg'),
     '-pyN.N.egg',
    ),
    (re.compile("user '%s'" % user), "user 'USER'"),
    (re.compile("group '%s'" % group), "group 'GROUP'"),
    (re.compile("%s %s" % (user, group)), "USER GROUP"),
    (re.compile(user), "USER"),
    ])


def test_suite():
    return unittest.TestSuite(
        doctest.DocFileSuite('README.rst', 'regression.txt',
            setUp=setUp, tearDown=zc.buildout.testing.buildoutTearDown,
            optionflags=doctest.ELLIPSIS, checker=checker),
        )
