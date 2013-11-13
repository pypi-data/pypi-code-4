# -*- coding: utf-8 -*-
"""
    sphinxcontrib.trydoc.quickstart
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    Quickly setup Tryton documentation source to work with Sphinx.

    :copyright: Copyright 2013 by the NaN·tic team, see AUTHORS.
    :license: GPL3, see LICENSE for details.
"""

import os
import re
import sys
import time
from os import path
from codecs import open

TERM_ENCODING = getattr(sys.stdin, 'encoding', None)

from sphinx import __version__
from sphinx.util.osutil import make_filename
from sphinx.util.console import (purple, bold, red, turquoise,
    nocolor, color_terminal)
from sphinx.util import texescape

# function to get input from terminal -- overridden by the test suite
try:
    # this raw_input is not converted by 2to3
    term_input = raw_input
except NameError:
    term_input = input


PROMPT_PREFIX = '> '
SOURCES_DIR = path.dirname(__file__)

if sys.version_info >= (3, 0):
    # prevents that the file is checked for being written in Python 2.x syntax
    QUICKSTART_CONF = '#!/usr/bin/env python3\n'
else:
    QUICKSTART_CONF = ''

with open('%s/conf.py.template' % SOURCES_DIR) as template_file:
    QUICKSTART_CONF += template_file.read()

with open('%s/Makefile.template' % SOURCES_DIR) as template_file:
    MAKEFILE = template_file.read()

MODULESCFG_FILE = '''[modules]

'''


def mkdir_p(dir):
    if path.isdir(dir):
        return
    os.makedirs(dir)


class ValidationError(Exception):
    """Raised for validation errors."""


def is_path(x):
    if path.exists(x) and not path.isdir(x):
        raise ValidationError("Please enter a valid path name.")
    return x


def nonempty(x):
    if not x:
        raise ValidationError("Please enter some text.")
    return x


def choice(*l):
    def val(x):
        if x not in l:
            raise ValidationError('Please enter one of %s.' % ', '.join(l))
        return x
    return val


def boolean(x):
    if x.upper() not in ('Y', 'YES', 'N', 'NO'):
        raise ValidationError("Please enter either 'y' or 'n'.")
    return x.upper() in ('Y', 'YES')


def suffix(x):
    if not (x[0:1] == '.' and len(x) > 1):
        raise ValidationError("Please enter a file suffix, "
                              "e.g. '.rst' or '.txt'.")
    return x


def ok(x):
    return x


def do_prompt(d, key, text, default=None, validator=nonempty):
    while True:
        if default:
            prompt = purple(PROMPT_PREFIX + '%s [%s]: ' % (text, default))
        else:
            prompt = purple(PROMPT_PREFIX + text + ': ')
        x = term_input(prompt)
        if default and not x:
            x = default
        if not isinstance(x, unicode):
            # for Python 2.x, try to get a Unicode string out of it
            if x.decode('ascii', 'replace').encode('ascii', 'replace') != x:
                if TERM_ENCODING:
                    x = x.decode(TERM_ENCODING)
                else:
                    print turquoise('* Note: non-ASCII characters entered '
                                    'and terminal encoding unknown -- '
                                    'assuming UTF-8 or Latin-1.')
                    try:
                        x = x.decode('utf-8')
                    except UnicodeDecodeError:
                        x = x.decode('latin1')
        try:
            x = validator(x)
        except ValidationError, err:
            print red('* ' + str(err))
            continue
        break
    d[key] = x


if sys.version_info >= (3, 0):
    # remove Unicode literal prefixes
    _unicode_string_re = re.compile(r"[uU]('.*?')")

    def _convert_python_source(source):
        return _unicode_string_re.sub('\1', source)

    globals()['QUICKSTART_CONF'] = _convert_python_source(
                globals()['QUICKSTART_CONF'])

    del _unicode_string_re, _convert_python_source


def ask_user(d):
    """Ask the user for quickstart values missing from *d*.

    Values are:

    * lang:      language code
    * path:      root path
    * sep:       separate source and build dirs (bool)
    * dot:       replacement for dot in _templates etc.
    * project:   project name
    * author:    author names
    * version:   version of project
    * release:   release of project
    * suffix:    source file suffix
    * inheritance_debug debug messages from inheritance extension on Makefile execution
    * verbose    more verbose messages on Makefile execution
    * set_trytond_params parameters for preoteus.config.set_trytond() call
    * master:    master document name
    * ext_*:     extensions to use (bools)
    * makefile:  make Makefile
    """

    print bold('Welcome to the Trydoc %s quickstart utility.') % __version__
    print '''
Please enter values for the following settings (just press Enter to
accept a default value, if one is given in brackets).'''

    if 'lang' in d:
        print bold('''
Selected language: %s''' % d['lang'])
    else:
        print '''
Enter the language code for documentation.'''
        do_prompt(d, 'lang', 'Language code for the documentation', 'es',
                choice(['es']))
    while not path.isfile('%s/index.rst.%s.template'
            % (SOURCES_DIR, d['lang'])):
        print
        print bold('Error: do not exist a template of master file (index.rst) '
            'for the selected language.')
        do_prompt(d, 'lang', 'Language code for the documentation', 'es',
                choice('es'))
        if not d['lang']:
            sys.exit(1)

    if 'path' in d:
        print bold('''
Selected root path: %s''' % d['path'])
    else:
        print '''
Enter the root path for documentation.'''
        do_prompt(d, 'path', 'Root path for the documentation', '.', is_path)

    while path.isfile(path.join(d['path'], 'conf.py')) or \
          path.isfile(path.join(d['path'], 'source', 'conf.py')):
        print
        print bold('Error: an existing conf.py has been found in the '
                   'selected root path.')
        print 'trydoc-quickstart will not overwrite existing Sphinx projects.'
        print
        do_prompt(d, 'path', 'Please enter a new root path (or just Enter '
                  'to exit)', '', is_path)
        if not d['path']:
            sys.exit(1)

    if 'sep' not in d:
        print '''
You have two options for placing the build directory for Sphinx output.
Either, you use a directory "_build" within the root path, or you separate
"source" and "build" directories within the root path.'''
        do_prompt(d, 'sep', 'Separate source and build directories (y/N)', 'n',
                  boolean)

    if 'dot' not in d:
        print '''
Inside the root directory, two more directories will be created; "_templates"
for custom HTML templates and "_static" for custom stylesheets and other static
files. You can enter another prefix (such as ".") to replace the underscore.'''
        do_prompt(d, 'dot', 'Name prefix for templates and static dir', '_',
            ok)

    if 'project' not in d:
        print '''
The project name will occur in several places in the built documentation.'''
        do_prompt(d, 'project', 'Project name')
    if 'author' not in d:
        do_prompt(d, 'author', 'Author name(s)')

    if 'version' not in d:
        print '''
Sphinx has the notion of a "version" and a "release" for the
software. Each version can have multiple releases. For example, for
Python the version is something like 2.5 or 3.0, while the release is
something like 2.5.1 or 3.0a1.  If you don't need this dual structure,
just set both to the same value.'''
        do_prompt(d, 'version', 'Project version', '1.0')
    if 'release' not in d:
        do_prompt(d, 'release', 'Project release', d['version'])

    if 'suffix' not in d:
        print '''
The file name suffix for source files. Commonly, this is either ".txt"
or ".rst".  Only files with this suffix are considered documents.'''
        do_prompt(d, 'suffix', 'Source file suffix', '.rst', suffix)

    if 'master' not in d:
        print '''
One document is special in that it is considered the top node of the
"contents tree", that is, it is the root of the hierarchical structure
of the documents. Normally, this is "index", but if your "index"
document is a custom template, you can also set this to another filename.'''
        do_prompt(d, 'master', 'Name of your master document (without suffix)',
                  'index')

    while (path.isfile(path.join(d['path'], d['master'] + d['suffix'])) or
          path.isfile(path.join(d['path'], 'source',
                d['master'] + d['suffix']))):
        print
        print bold('Error: the master file %s has already been found in the '
                   'selected root path.' % (d['master'] + d['suffix']))
        print 'trydoc-quickstart will not overwrite the existing file.'
        print
        do_prompt(d, 'master', 'Please enter a new file name, or rename the '
                  'existing file and press Enter', d['master'])

#    if 'ext_autodoc' not in d:
#        print '''
#Please indicate if you want to use one of the following Sphinx extensions:'''
#        do_prompt(d, 'ext_autodoc', 'autodoc: automatically insert docstrings '
#                  'from modules (y/N)', 'n', boolean)
#    if 'ext_doctest' not in d:
#        do_prompt(d, 'ext_doctest', 'doctest: automatically test code '
#                  'snippets in doctest blocks (y/N)', 'n', boolean)
#    if 'ext_todo' not in d:
#        do_prompt(d, 'ext_todo', 'todo: write "todo" entries '
#                  'that can be shown or hidden on build (y/N)', 'n', boolean)
#    if 'ext_coverage' not in d:
#        do_prompt(d, 'ext_coverage', 'coverage: checks for documentation '
#                  'coverage (y/N)', 'n', boolean)
#    if 'ext_pngmath' not in d:
#        do_prompt(d, 'ext_pngmath', 'pngmath: include math, rendered '
#                  'as PNG images (y/N)', 'n', boolean)
#    if 'ext_mathjax' not in d:
#        do_prompt(d, 'ext_mathjax', 'mathjax: include math, rendered in the '
#                  'browser by MathJax (y/N)', 'n', boolean)
#    if d['ext_pngmath'] and d['ext_mathjax']:
#        print '''Note: pngmath and mathjax cannot be enabled at the same time.
#pngmath has been deselected.'''
#    if 'ext_ifconfig' not in d:
#        do_prompt(d, 'ext_ifconfig', 'ifconfig: conditional inclusion of '
#                  'content based on config values (y/N)', 'n', boolean)
#    if 'ext_viewcode' not in d:
#        do_prompt(d, 'ext_viewcode', 'viewcode: include links to the source '
#                  'code of documented Python objects (y/N)', 'n', boolean)

    if 'makefile' not in d:
        print '''
A Makefile and a Windows command file can be generated for you so that you
only have to run e.g. `make html' instead of invoking sphinx-build
directly.'''
        do_prompt(d, 'makefile', 'Create Makefile? (Y/n)', 'y', boolean)
    print

    if 'inheritance_debug' not in d:
        print '''
Do you want more verbose messages from sphinxcontrib-inheritance extension when
execute the Makefile? It is useful if you are developing it or you have any bug
to report.'''
        do_prompt(d, 'inheritance_debug',
            'Enable sphinxcontrib-inheritance debug messages (y/N)', 'n',
            boolean)
        print

    if 'verbose' not in d:
        print '''
Do you want more verbose messages from sphinxcontrib-inheritance and trydoc
extension when execute the Makefile? It is useful if you are developing them or
you have any bug to report.'''
        do_prompt(d, 'verbose',
            'More verbose messages on Makefile execution (y/N)', 'n', boolean)
        print

    if 'set_trytond_params' not in d:
        print '''
A persistent database is recommended in production environment to get the field
names, menus and other dynamic information exactly as the customers are
viewing.
If you choose No, a SQLite with the selected modules will be created each time
to generate the manual.'''
        do_prompt(d, 'persistent',
            'Use a persistent database to generate the manual (Y/n)', 'y',
                boolean)
        if not d['persistent']:
            d['set_trytond_params'] = "database_type='sqlite'"
        else:
            print '''
Write the database name of the customer for who is this manual to use it to
generate the dynamic information as field names, menus...'''
            do_prompt(d, 'database', 'Database')
            print

            print '''
The admin password is required to connect to database.'''
            do_prompt(d, 'admin_password', 'Admin password')
            print

            d['set_trytond_params'] = (
                "'%s', database_type='postgresql', password='%s'"
                % (d['database'], d['admin_password']))
            del d['database']
            del d['admin_password']
        d['persistent']

    if 'trytond_installed' not in d:
        print '''
If trytond is not installed as a Python module you must to provide the path to
trytond directory to could be set into the system path.'''
        do_prompt(d, 'trytond_installed',
            'Is trytond installed as a Python module? (y/N)', 'n', boolean)
        if d['trytond_installed']:
            d['trytond_into_path'] = ''
        else:
            print '''
    Enter the root path for documentation.'''
            do_prompt(d, 'trytond_directory', 'Path to the trytond directory',
                '../trytond', is_path)
            print

            d['trytond_directory'] = (
                path.relpath(d['trytond_directory'], d['path']))

            d['trytond_into_path'] = '''sys.path.insert(0, '%s')
''' % d['trytond_directory']
        del d['trytond_directory']
    del d['trytond_installed']


def generate(d, overwrite=True, silent=False):
    """Generate project based on values in *d*."""

    texescape.init()

    if 'mastertoctree' not in d:
        d['mastertoctree'] = ''
    if 'mastertocmaxdepth' not in d:
        d['mastertocmaxdepth'] = 2

    d['project_fn'] = make_filename(d['project'])
    d['project_manpage'] = d['project_fn'].lower()
    d['now'] = time.asctime()
    d['project_underline'] = len(d['project']) * '='
    d['extensions'] = ', '.join(
        repr('sphinxcontrib.' + name) for name in ('inheritance', 'trydoc'))
    #d['extensions'] = ', '.join(
    #    repr('sphinx.ext.' + name)
    #    for name in ('autodoc', 'doctest', 'todo', 'coverage',
    #                 'pngmath', 'mathjax', 'ifconfig', 'viewcode')
    #    if d.get('ext_' + name))
    d['copyright'] = time.strftime('%Y') + ', ' + d['author']
    d['author_texescaped'] = unicode(d['author']).\
                             translate(texescape.tex_escape_map)
    d['project_doc'] = d['project'] + ' Documentation'
    d['project_doc_texescaped'] = unicode(d['project'] + ' Documentation').\
                                  translate(texescape.tex_escape_map)

    # escape backslashes and single quotes in strings that are put into
    # a Python string literal
    for key in ('project', 'project_doc', 'project_doc_texescaped',
                'author', 'author_texescaped', 'copyright',
                'version', 'release', 'master'):
        d[key + '_str'] = d[key].replace('\\', '\\\\').replace("'", "\\'")

    if not path.isdir(d['path']):
        mkdir_p(d['path'])

    srcdir = d['sep'] and path.join(d['path'], 'source') or d['path']

    mkdir_p(srcdir)
    if d['sep']:
        builddir = path.join(d['path'], 'build')
        d['exclude_patterns'] = ''
    else:
        builddir = path.join(srcdir, d['dot'] + 'build')
        d['exclude_patterns'] = repr(d['dot'] + 'build')
    mkdir_p(builddir)
    mkdir_p(path.join(srcdir, d['dot'] + 'templates'))
    mkdir_p(path.join(srcdir, d['dot'] + 'static'))

    def write_file(fpath, mode, content):
        if overwrite or not path.isfile(fpath):
            print 'Creating file %s.' % fpath
            f = open(fpath, mode, encoding='utf-8')
            try:
                f.write(content)
            finally:
                f.close()
        else:
            print 'File %s already exists, skipping.' % fpath

    conf_text = QUICKSTART_CONF % d

    write_file(path.join(srcdir, 'conf.py'), 'w', conf_text)

    with open('%s/index.rst.%s.template' % (SOURCES_DIR, d['lang'])
              ) as template_file:
        MASTER_FILE = template_file.read()

    masterfile = path.join(srcdir, d['master'] + d['suffix'])
    write_file(masterfile, 'w', MASTER_FILE % d)

    modulescfgfile = path.join(srcdir, 'modules.cfg')
    write_file(modulescfgfile, 'w', MODULESCFG_FILE)

    if d['makefile']:
        d['rsrcdir'] = d['sep'] and 'source' or '.'
        d['rbuilddir'] = d['sep'] and 'build' or d['dot'] + 'build'
        # use binary mode, to avoid writing \r\n on Windows
        write_file(path.join(d['path'], 'Makefile'), 'wb', MAKEFILE % d)

    if silent:
        return
    print
    print bold('Finished: An initial directory structure has been created.')
    print '''
You should now populate the directory with symlinks to Tryton modules localized
documentation.
Use the trydoc-symlinks utility:
    trydoc-symlinks %s PATH_TO_modules_DIR %s
    trydoc-symlinks --no-remove %s PATH_TO_trytond_doc_DIR %s

After that, you can populate the modules.cfg file with the list of modules to
include in the manual. It should be the installed modules in the customer's
database.
Use the trydoc-update-modules utility. Look the help:
    trydoc-update-modules --help

At the end, ''' % (d['lang'], d['path'], d['lang'], d['path']) + (d['makefile']
    and '''use the Makefile to build the docs, like so:
   make builder
''' or '''use the sphinx-build command to build the docs, like so:
   sphinx-build -b builder %s %s
''' % (srcdir, builddir)) + '''\
where "builder" is one of the supported builders, e.g. html, latex or linkcheck.
'''


def main(argv=sys.argv):
    if not color_terminal():
        nocolor()

    d = {}
    if len(argv) < 2 or len(argv) > 3:
        print 'Usage: trydoc-quickstart lang_code [root]'
        sys.exit(1)
    elif len(argv) == 3:
        d['path'] = argv[2]
    d['lang'] = argv[1]
    try:
        ask_user(d)
    except (KeyboardInterrupt, EOFError):
        print
        print '[Interrupted.]'
        return
    generate(d)
