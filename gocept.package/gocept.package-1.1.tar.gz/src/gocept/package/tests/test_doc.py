# Copyright (c) 2012 gocept gmbh & co. kg
# See also LICENSE.txt

import gocept.package.doc
import gocept.testing.assertion
import os.path
import shutil
import subprocess
import sys
import tempfile
import unittest2 as unittest


class DocBuildEndtoend(unittest.TestCase, gocept.testing.assertion.Ellipsis):

    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.cwd = os.getcwd()
        os.chdir(self.tmpdir)
        self.mkdir('src')
        self.write('setup.py', """\
from setuptools import setup

setup(
    name='testpackage',
    version='1.0',
    author='Author',
    package_dir={'': 'src'},
)
""")
        subprocess.call([sys.executable, 'setup.py', 'egg_info'])
        self.mkdir('doc')
        self.write('doc/api.txt', 'dummy')

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmpdir)

    def mkdir(self, path):
        os.mkdir(os.path.join(self.tmpdir, path))

    def write(self, path, contents):
        with open(os.path.join(self.tmpdir, path), 'w') as f:
            f.write(contents)

    def test_should_generate_documentation(self):
        self.write('doc/conf.py', """\
import gocept.package.sphinxconf
gocept.package.sphinxconf.set_defaults()
""")
        self.write('doc/index.txt', 'foo and bar and qux')
        gocept.package.doc.main(['doc'])
        index_html = os.path.join(self.tmpdir, 'build/doc/index.html')
        self.assertTrue(os.path.isfile(index_html))
        contents = open(index_html).read()
        self.assertEllipsis('...foo and bar and qux...', contents)

    def test_variables_from_confpy_are_available_in_sphinxconf_module(self):
        self.write('doc/conf.py', """\
import gocept.package.sphinxconf

_year_started = 2000
gocept.package.sphinxconf.set_defaults()
        """)
        self.write('doc/index.txt', 'foo and bar and qux')
        gocept.package.doc.main(['doc'])
        index_html = os.path.join(self.tmpdir, 'build/doc/index.html')
        contents = open(index_html).read()
        self.assertEllipsis('...Copyright 2000-2...', contents)

    def test_defaults_from_sphinxconf_should_not_override_confpy(self):
        self.write('doc/conf.py', """\
import gocept.package.sphinxconf

release = '2.0beta'
gocept.package.sphinxconf.set_defaults()
        """)
        self.write('doc/index.txt', 'foo and bar and qux')
        gocept.package.doc.main(['doc'])
        index_html = os.path.join(self.tmpdir, 'build/doc/index.html')
        contents = open(index_html).read()
        self.assertEllipsis('...testpackage v2.0beta...', contents)

    def test_command_line_arguments_are_passed_to_sphinx_build(self):
        self.write('doc/conf.py', """\
import gocept.package.sphinxconf

release = '2.0beta'
gocept.package.sphinxconf.set_defaults()
        """)
        self.write('doc/index.txt', 'foo and bar and qux')
        gocept.package.doc.main(['doc', '-D', 'release=3.1.4'])
        index_html = os.path.join(self.tmpdir, 'build/doc/index.html')
        contents = open(index_html).read()
        self.assertEllipsis('...testpackage v3.1.4...', contents)
