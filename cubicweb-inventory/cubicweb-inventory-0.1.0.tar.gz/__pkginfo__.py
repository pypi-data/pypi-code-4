# pylint: disable-msg=W0622
"""cubicweb-inventory packaging information"""

modname = 'inventory'
distname = "cubicweb-inventory"

numversion = (0, 1, 0)
version = '.'.join(str(num) for num in numversion)

license = 'LGPL'
copyright = '''Copyright (c) 2003-2011 LOGILAB S.A. (Paris, FRANCE).
http://www.logilab.fr/ -- mailto:contact@logilab.fr'''
author = 'LOGILAB S.A. (Paris, FRANCE)'
author_email = 'contact@logilab.fr'

description = "Hardware inventory application based on the CubicWeb framework"

web = 'http://www.cubicweb.org/project/%s' % distname

classifiers = [
    'Environment :: Web Environment',
    'Framework :: CubicWeb',
    'Programming Language :: Python',
    'Programming Language :: JavaScript',
    ]

# dependencies
__depends__ = {'cubicweb': '>= 3.12.5',
               'cubicweb-zone': None,
               'cubicweb-folder': None,
               'cubicweb-comment': None,
               'cubicweb-link': None,
               'cubicweb-tag': None,
               'cubicweb-company': None,
               }

# packaging

from os import listdir as _listdir
from os.path import join, isdir, exists
from glob import glob

THIS_CUBE_DIR = join('share', 'cubicweb', 'cubes', modname)

def listdir(dirpath):
    return [join(dirpath, fname) for fname in _listdir(dirpath)
            if fname[0] != '.' and not fname.endswith('.pyc')
            and not fname.endswith('~')
            and not isdir(join(dirpath, fname))]

data_files = [
    # common files
    [THIS_CUBE_DIR, [fname for fname in glob('*.py') if fname != 'setup.py']],
    ]
# check for possible extended cube layout
for dname in ('entities', 'views', 'sobjects', 'hooks', 'schema', 'data', 'wdoc', 'i18n', 'migration', 'scripts'):
    if isdir(dname):
        data_files.append([join(THIS_CUBE_DIR, dname), listdir(dname)])
# Note: here, you'll need to add subdirectories if you want
# them to be included in the debian package
