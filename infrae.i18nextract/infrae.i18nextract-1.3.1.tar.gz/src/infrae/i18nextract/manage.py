# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id: manage.py 50858 2013-05-23 11:19:23Z sylvain $

from optparse import OptionParser
import os
import re
import sys
import tarfile

from zope.configuration.name import resolve
from infrae.i18nextract.utils import load_products


po_file_reg = re.compile('^(.*)-([a-zA-Z_]{2,5})\.po$')
tar_file_reg = re.compile('^([^/]*)/.*-([a-zA-Z_]{2,5})\.po$')


def export_tarball(tarball, path, domain, pot_only=False):
    tar = tarfile.open(tarball, "w:gz")
    pot_file = os.path.join(path, domain + '.pot')
    if os.path.isfile(pot_file):
        tar.add(pot_file, arcname=domain + '/' + domain + '.pot')

    if pot_only:
        tar.close()
        return

    for language in os.listdir(path):
        po_file = os.path.join(path, language, 'LC_MESSAGES', domain + '.po')
        if not os.path.isfile(po_file):
            continue
        tar.add(po_file, arcname=domain + '/' + language + '.po')

    tar.close()


def import_tarball(tarball, path, options):
    if not os.path.isfile(tarball):
        print "Invalid import tarball: ", tarball
        sys.exit(-1)

    tar = tarfile.open(tarball, "r:gz")
    for name in tar.getnames():
        if name.endswith('.po'):
            match = tar_file_reg.search(name)
            if not match:
                continue # not a .po file
            domain = match.group(1)
            language = match.group(2)

            language_path = os.path.join(path, language)
            if not os.path.isdir(language_path):
                os.mkdir(language_path)
            lc_messages_path = os.path.join(language_path, 'LC_MESSAGES')
            if not os.path.isdir(lc_messages_path):
                os.mkdir(lc_messages_path)
            po_path = os.path.join(lc_messages_path, domain + '.po')
            mo_path = os.path.join(lc_messages_path, domain + '.mo')

            content = tar.extractfile(name).read()
            po_file = open(po_path, 'w')
            print 'Extracting language "%s", domain "%s"' % (
                language, domain)
            po_file.write(content)
            po_file.close()

            if options.compile:
                print 'Compiling language "%s", domain "%s".' % (
                    language, domain)
                os.system('msgfmt -o %s %s' % (mo_path, po_path))

    tar.close()


def merge_or_compile_files(path, options):
    for filename in os.listdir(path):
        filename = os.path.join(path, filename)
        if filename.endswith('.po'):
            match = po_file_reg.search(filename)
            if not match:
                # not a .po file
                continue
            domain = match.group(1)
            language = match.group(2)
            pot_path = os.path.join(path, '%s.pot' % domain)
            if options.merge:
                print 'Merging language "%s", domain "%s"' % (language, domain)
                os.system('msgmerge -N -U %s %s' %(filename, pot_path))
            if options.compile:
                compiled_filename = os.path.splitext(filename)[0] + '.mo'
                print 'Compiling language "%s", domain "%s".' % (
                    language, domain)
                os.system('msgfmt -o %s %s' % (compiled_filename, filename))

    for language in os.listdir(path):
        lc_messages_path = os.path.join(path, language, 'LC_MESSAGES')

        # Make sure we got a language directory
        if not os.path.isdir(lc_messages_path):
            continue

        for filename in os.listdir(lc_messages_path):
            if filename.endswith('.po'):
                pot_path = os.path.join(path, filename + 't')
                domain = '.'.join(filename.split('.')[:-1])
                filename = os.path.join(lc_messages_path, filename)
                if options.merge:
                    print 'Merging language "%s", domain "%s"' % (
                        language, domain)
                    os.system('msgmerge -N -U %s %s' %(filename, pot_path))
                if options.compile:
                    compiled_filename = os.path.splitext(filename)[0] + '.mo'
                    print 'Compiling language "%s", domain "%s".' % (
                        language, domain)
                    os.system('msgfmt -o %s %s' % (compiled_filename, filename))


def manage(output_package, products, domain):
    """Merge translations for the given packages.
    """
    parser = OptionParser()
    parser.add_option(
        "-p", "--path", dest="path",
        help=("path where the translation to merge are, "
              "default to the package '%s'" % output_package))
    parser.add_option(
        "-c", "--compile", dest="compile", action="store_true",
        help="compile all translation files")
    parser.add_option(
        "-m", "--merge", dest="merge", action="store_true",
        help="merge all templates to in all translation files")
    parser.add_option(
        "-i", "--import-tarball", dest="import_tarball",
        help=("the translations are packed in a tarball, "
              "and will be imported in the package '%s'" % output_package))
    parser.add_option(
        "-e", "--export-tarball", dest="export_tarball",
        help=("a tarball will be created containing the translations"))
    parser.add_option(
        "--pot-only", dest="pot_only", action='store_true', default=False,
        help=("apply the action only on the pot file"))
    (options, args) = parser.parse_args()

    if products:
        load_products(products)
    if options.path:
        path = options.path
    else:
        python_package = resolve(output_package)
        path = os.path.dirname(python_package.__file__)

    for i18n_part in ('i18n', 'locales'):
        i18n_path = os.path.join(path, i18n_part)
        if os.path.isdir(i18n_path):
            print "Processing package %s..." % i18n_path
            if options.import_tarball:
                import_tarball(options.import_tarball, i18n_path, options)
            elif options.export_tarball:
                export_tarball(
                    options.export_tarball, i18n_path, domain,
                    pot_only=options.pot_only)
            else:
                merge_or_compile_files(i18n_path, options)


def egg_entry_point(kwargs):
    return manage(**kwargs)
