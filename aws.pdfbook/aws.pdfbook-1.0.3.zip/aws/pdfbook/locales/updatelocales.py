# -*- coding: utf-8 -*-
# $Id: updatelocales.py 117340 2010-05-12 09:15:25Z glenfant $
"""
i18n files maintenance utility. Please read the README.txt beside this
file.  Portions of this code have been stolen from
PlacelessTranslationService to prevent PYTHONPATH issues
"""

import os
import sys

from i18ndude.script import rebuild_pot as i18n_rebuild_pot
from i18ndude.script import sync as i18n_sync

###
## START OF CUSTOMIZABLE SECTION
###

# Set this to True to get verbosity and keep temporary files if any
DEBUG = True

# Your main translation domain
DOMAIN = 'aws.pdfbook'

# Directories excluded from i18n markup search
EXCLUDED = ['profiles', 'tests']

###
## END OF CUSTOMIZABLE SECTION
###

THIS_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GENERATED_POT = '%s.pot' % DOMAIN
MANUAL_POT = '%s-manual.pot' % DOMAIN
if os.path.exists(MANUAL_POT):
    MERGE_OPT = ['--merge', MANUAL_POT]
else:
    MERGE_OPT = []
if EXCLUDED:
    EXCLUDED_OPT = '--exclude="%s"' % ' '.join(EXCLUDED)
else:
    EXCLUDED_OPT = ''
PO_FILENAME = '%s.po' % DOMAIN

def main():

    # Rebuilding the <domain>.pot
    if DEBUG:
        print "Rebuilding", GENERATED_POT
    argv = [
        'i18ndude', 'rebuild-pot',
        '--pot', GENERATED_POT,
        '--create', DOMAIN,
        MERGE_OPT,
        EXCLUDED_OPT,
        ROOT]
    sys.argv = flatten(argv)
    i18n_rebuild_pot()

    # Synching the .po files
    if DEBUG:
        print "Synching", PO_FILENAME, "files"
    argv = [
        'i18ndude', 'sync',
        '--pot', GENERATED_POT,
        find_po_files()
        ]
    sys.argv = flatten(argv)
    i18n_sync()

    return

def flatten(seq):
    """
    >>> flatten([0, [1, 2, 3], [4, 5, [6, 7]]])
    [0, 1, 2, 3, 4, 5, 6, 7]
    """
    out = []
    for item in seq:
        if isinstance(item, (list, tuple)):
            out.extend(flatten(item))
        elif item:
            out.append(item)
    return out

def find_po_files():
    """List of abs paths to .po files"""
    po_files = []
    for root, dirs, files in os.walk(THIS_DIR):
        # Don' visit CSV or SVN marker dirs
        for blacklisted in ('CVS', '.svn'):
            if blacklisted in dirs:
                dirs.remove(blacklisted)
        if PO_FILENAME in files:
            po_files.append(os.path.join(root, PO_FILENAME))
    return po_files


if __name__ == '__main__':
    main()
