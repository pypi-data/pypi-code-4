# -*- coding: utf-8 -*-
# Copyright (c) 2010-2013 Infrae. All rights reserved.
# See also LICENSE.txt
# $Id$

import os
from optparse import OptionParser

from zope.configuration.name import resolve
from zope.app.locales.extract import POTMaker, POTEntry, py_strings, tal_strings
from infrae.i18nextract.formulator_extract import formulator_strings
from infrae.i18nextract.metadata_extract import metadata_strings
from infrae.i18nextract.utils import load_products


class MultiplePOTMaker(POTMaker):
    """This class inserts sets of strings into a POT file.
    """

    def add(self, strings, base_dir=None, package=None):
        for msgid, locations in strings.items():
            if msgid == '':
                continue
            if msgid not in self.catalog:
                self.catalog[msgid] = POTEntry(msgid)

            for filename, lineno in locations:
                if base_dir is not None:
                    filename = filename.replace(base_dir, '')
                if package is not None:
                    filename = '%s:%s' % (package, filename)
                self.catalog[msgid].addLocationComment(filename, lineno)

    def _getProductVersion(self):
        return '1.0'


def extract(packages, output_dir, output_package, domain, products):
    """Extract i18n strings
    """
    parser = OptionParser()
    parser.add_option(
        "-o", "--output", dest="output_dir",
        help="alternate output directory for the extracted file")
    parser.add_option(
        "-p", "--package", action="store_true", dest="output_package",
        help="extract to the output package")
    (options, args) = parser.parse_args()

    if products:
        load_products(products)

    output_file = domain + '.pot'
    if options.output_dir:
        if not os.path.exists(options.output_dir):
            print "Selected directory doesn't exists: %s" % options.output_dir
            return
        output_file = os.path.join(options.output_dir, output_file)
    elif options.output_package:
        if not output_package:
            print "No output package selected."
            return
        python_package = resolve(output_package)
        path = os.path.join(os.path.dirname(python_package.__file__), 'i18n')
        if not os.path.exists(path):
            print "Selected package doesn't have translations: %s" % path
            return
        output_file = os.path.join(path, output_file)
    elif output_dir:
        if not os.path.exists(output_dir):
            os.mkdir(output_dir)
        output_file = os.path.join(output_dir, output_file)

    print "Domain: %s" % domain
    print "Output file: %r" % output_file

    maker = MultiplePOTMaker(output_file, '')
    for package in packages:
        print "Processing package %s..." % package
        python_package = resolve(package)
        path = os.path.dirname(python_package.__file__)

        maker.add(py_strings(path, domain), path, package)
        maker.add(tal_strings(path, domain), path, package)
        # For Chameleon templates
        maker.add(tal_strings(path, domain, filePattern='*.cpt'), path, package)
        maker.add(formulator_strings(path, domain), path, package)
        maker.add(metadata_strings(path, domain), path, package)
    maker.write()

    return output_file


def egg_entry_point(kwargs):
    return extract(**kwargs)
