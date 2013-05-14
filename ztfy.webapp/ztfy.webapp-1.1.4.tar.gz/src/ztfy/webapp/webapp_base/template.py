##############################################################################
#
# Copyright (c) 2010 Zope Foundation and Contributors.
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
from HTMLParser import HTMLParser
from paste.script import templates
from paste.script.templates import var
from urllib2 import urlopen
import pkg_resources
import re, os, sys

DOWNLOAD_URL = 'http://download.ztfy.org/webapp/'

class FindLatest(HTMLParser):
    """html parser used to find the latest version file on download.zope.org
    """
    def reset(self):
        """initialize a regexp and a version set"""
        HTMLParser.reset(self)
        self.regexp = re.compile('.*ztfy.webapp-(.*).cfg$')
        self.versions = set()

    def handle_starttag(self, tag, attrs):
        """extract the version from each link"""
        if tag != 'a':
            return
        for attr in attrs:
            if attr[0] == 'href' and self.regexp.match(attr[1]):
                self.versions.add(self.regexp.sub('\\1', attr[1]))


class Webapp(templates.Template):
    """ The main paster template for ZTFY.webapp
    """
    _template_dir = 'webapp_template'
    summary = "A ZTFY webapp project, referencing all ZTFY packages"

    vars = [
        var('python_package',
            u'Main Python package (without namespace)'),
        var('interpreter',
            u'Name of custom Python interpreter',
            default='ztpy'),
        var('release', (u'Which release of ZTFY.webapp?\n'
                        u'Check on %s' % DOWNLOAD_URL)),
        var('version', u'Version of your project', default='0.1'),
        var('description', u'One-line description of the package'),
        var('long_description', u'Multi-line description (in reST)'),
        var('keywords', u'Space-separated keywords/tags'),
        var('author', u'Author name'),
        var('author_email', u'Author email'),
        var('url', u'URL of homepage'),
        var('license_name', u'License name'),
        ]

    def check_vars(self, vars, cmd):
        """This method checks the variables and ask for missing ones
        """
        # Find the latest versions.cfg online
        current = pkg_resources.get_distribution('ztfy.webapp').version
        latest = current
        try:
            if 'offline' not in vars:  #offline is used in tests
                sys.stdout.write('Searching the latest version... ')
                sys.stdout.flush()
                parse_version = pkg_resources.parse_version

                # download and parse the html page and store versions
                parser = FindLatest()
                parser.feed(urlopen(DOWNLOAD_URL).read())

                # return the highest minor version
                if not len(parser.versions):
                    raise IOError('No versions found')
                all_versions = sorted(parser.versions,
                                      key=lambda v: parse_version(v),
                                      reverse=True)
                for v in all_versions:
                    trunked_v = [x for x in parse_version(v)[:2] if not x.startswith('*')]
                    trunked_current = [x for x in parse_version(current)[:2] if not x.startswith('*')]
                    while len(trunked_v) < 2:
                        trunked_v.append('00000000')
                    while len(trunked_current) < 2:
                        trunked_current.append('00000000')
                    if trunked_v > trunked_current:
                        continue
                    latest = v
                    break

                print str(latest) + '\n'

                # warn the user if there is a change in the latest template
                last_change = '1.1.0' # feature introduced for 1.0b4
                for line in urlopen(DOWNLOAD_URL
                                    + 'ztfy.webapp-%s.cfg' % latest).readlines():
                    if 'LAST_TEMPLATE_CHANGE' in line:
                        last_change = line.split('=')[1].strip()
                        break
                if parse_version(last_change) > parse_version(current):
                    print ('**WARNING**: the project template for ZTFY.webapp '
                           'has changed since version %s.\n'
                           'You should upgrade to this version.\n' % last_change)

        except IOError:
            # if something wrong occurs, we keep the current version
            print u'**WARNING**: error while getting the latest version online'
            print u'Please check that you can access %s\n' % DOWNLOAD_URL

        # suggest what Paste chose
        for var in self.vars:
            if var.name == 'release':
                var.default = latest
            if var.name == 'python_package':
                var.default = vars['package']
                # but keep the user's input if there are dots in the middle
                if '.' in vars['project'][1:-1]:
                    var.default = re.sub('[^A-Za-z0-9.]+', '_',
                                         vars['project']).lower()

        # ask remaining variables
        vars = templates.Template.check_vars(self, vars, cmd)

        # replace Paste default choice with ours
        vars['package'] = vars['python_package']

        # check for bad python package names
        if vars['package'] in ('bluebream', 'bream', 'zope'):
            print
            print "Error: The chosen project name results in an invalid " \
                  "package name: %s." % vars['package']
            print "Please choose a different project name."
            sys.exit(1)
        vars['zip_safe'] = False
        # remember the version of bluebream used to create the project
        vars['created_with'] = current
        return vars

    def pre(self, command, output_dir, vars):
        """Detect namespaces in the project name
        """
        if not command.options.verbose:
            command.verbose = 0
        self.ns_split = vars['package'].split('.')
        vars['package'] = self.ns_split[-1]
        vars['namespace_packages'] = list(reversed([
                    vars['python_package'].rsplit('.', i)[0]
                    for i in range(1, len(self.ns_split))]))
        vars['ns_prefix'] = '.'.join(self.ns_split[:-1]) + '.'
        if len(self.ns_split) == 1:
            vars['ns_prefix'] = ''
        vars['basedir'] = os.getcwd()

    def post(self, command, output_dir, vars):
        """Add nested namespace levels
           and move the main package to the last level
        """
        # if we have a namespace package
        if len(self.ns_split) > 1:
            package_dir = os.path.join(output_dir, 'src', vars['package'])
            tmp_dir = package_dir + '.tmp'
            os.rename(package_dir, tmp_dir)

            # create the intermediate namespace packages
            target_dir = os.path.join(output_dir, 'src',
                                      os.path.join(*self.ns_split[:-1]))
            os.makedirs(target_dir)

            # create each __init__.py with namespace declaration
            ns_decl = "__import__('pkg_resources').declare_namespace(__name__)"
            for i, namespace_package in enumerate(self.ns_split[:-1]):
                init_file = os.path.join(output_dir, 'src',
                                         os.path.join(*self.ns_split[:i + 1]),
                                         '__init__.py')
                open(init_file, 'w').write(ns_decl)

            # move the (renamed) main package to the last namespace
            os.rename(tmp_dir,
                      os.path.join(target_dir, os.path.basename(package_dir,)))

        print("\nYour project has been created! Now, you want to:\n"
              "1) put the generated files under version control\n"
              "2) run: python bootstrap.py\n"
              "3) run: ./bin/buildout\n"
             )
