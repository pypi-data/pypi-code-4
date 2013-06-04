# Copyright (c) 2012-2013 gocept gmbh & co. kg
# See also LICENSE.txt

import datetime
import gocept.package
import gocept.package.doc
import gocept.package.sphinxconf
import gocept.testing.assertion
import os
import os.path
import paste.script.command
import pkginfo
import shutil
import subprocess
import sys
import tempfile
import time
import unittest2 as unittest


class SkeletonSetUp(unittest.TestCase):

    def setUp(self):
        self.cwd = os.getcwd()
        self.tmpdir = tempfile.mkdtemp()
        os.chdir(self.tmpdir)

    def tearDown(self):
        os.chdir(self.cwd)
        shutil.rmtree(self.tmpdir)

    def expand_template(self):
        try:
            paste.script.command.run(
                'create -t gocept-package gocept.example'.split() + [
                    'description="An example package." ',
                    'keywords="example package"',
                    ])
        except SystemExit:
            pass

    def content(self, rel_path):
        file_path = os.path.join(
            self.tmpdir, 'gocept.example', *rel_path.split('/'))
        self.assertTrue(os.path.isfile(file_path))
        return open(file_path).read()


class Skeleton(SkeletonSetUp, gocept.testing.assertion.Ellipsis):

    def test_expanding_template_creates_files(self):
        self.expand_template()
        self.assertEqual(
            '', self.content('src/gocept/example/tests/__init__.py'))
        self.assertIn(
            str(datetime.date.today().year), self.content('COPYRIGHT.txt'))

    def test_package_has_gocept_package_version_pinned_to_active(self):
        self.expand_template()
        gocept_package = pkginfo.Installed('gocept.package')
        self.assertIn('gocept.package = %s\n' % gocept_package.version,
                      self.content('versions/versions.cfg'))

    def test_hg_init_has_been_run(self):
        self.expand_template()
        self.assertTrue(os.path.isdir(os.path.join('gocept.example', '.hg')))

    def test_setup_py_is_functional(self):
        # paster detects setup.py and creates egg-info from it
        self.expand_template()
        self.assertIn('Name: gocept.example\n',
                      self.content('src/gocept.example.egg-info/PKG-INFO'))

    def test_sphinx_docs_can_be_built(self):
        self.expand_template()
        os.chdir('gocept.example')
        gocept.package.doc.main(['doc'])
        self.assertIn('<html', self.content('build/doc/index.html'))

    def test_project_links_are_fully_expanded_in_sphinx_sidebar(self):
        self.expand_template()
        os.chdir('gocept.example')
        gocept.package.doc.main(['doc'])
        self.assertEllipsis(
            '...<a href="https://bitbucket.org/gocept/gocept.example/">Project home</a>...',
            self.content('build/doc/index.html'))
        self.assertIn(
            '<a href="http://pypi.python.org/pypi/gocept.example/">PyPI</a>',
            self.content('build/doc/index.html'))

    def test_coveragerc_is_renamed_with_dot(self):
        self.expand_template()
        self.assertIn('source = gocept.example', self.content('.coveragerc'))


class Buildout(SkeletonSetUp):

    level = 2

    def setUp(self):
        super(Buildout, self).setUp()
        self.expand_template()
        os.chdir('gocept.example')

    @property
    def gocept_package_dev(self):
        path = gocept.package.__file__
        for _ in xrange(4):
            path = os.path.dirname(path)
        return path

    def buildout(self):
        subprocess.call([sys.executable, 'bootstrap.py'])
        return subprocess.call([
                os.path.join('bin', 'buildout'),
                'buildout:develop+=%s' % self.gocept_package_dev])

    def test_bootstrap_succeeds_using_distribute_by_default(self):
        subprocess.call([sys.executable, 'bootstrap.py'])
        bin_buildout = self.content('bin/buildout')
        self.assertIn(sys.executable, bin_buildout)
        self.assertIn('distribute-', bin_buildout)
        self.assertNotIn('setuptools-', bin_buildout)

    def test_buildout_succeeds(self):
        status = self.buildout()
        self.assertEqual(0, status)
        self.assertEqual(
            ['buildout', 'doc', 'test'], sorted(os.listdir('bin')))

    def test_tests_succeed(self):
        self.buildout()
        bin_test = os.path.join('bin', 'test')
        self.assertTrue(os.path.isfile(bin_test))
        status = subprocess.call([bin_test])
        self.assertEqual(0, status)

    def test_sphinx_docs_can_be_built(self):
        self.buildout()
        bin_doc = os.path.join('bin', 'doc')
        self.assertTrue(os.path.isfile(bin_doc))
        subprocess.call([bin_doc])
        self.assertIn('<html', self.content('build/doc/index.html'))

    def test_sphinx_api_docs_are_updated_with_every_run(self):
        self.buildout()
        bin_doc = os.path.join('bin', 'doc')
        api_txt = open(os.path.join('doc', 'api.txt'), 'w')
        api_txt.write("""\
.. autosummary::
    :toctree: %s

    gocept.example.foo
""" % gocept.package.sphinxconf.AUTOSUMMARY_OUTPUT)
        api_txt.close()
        foo_py = open(os.path.join('src', 'gocept', 'example', 'foo.py'), 'w')
        foo_py.write('"A module doc string."')
        foo_py.close()
        subprocess.call([bin_doc])
        self.assertIn('A module doc string.',
                      self.content('build/doc/_api/gocept.example.foo.html'))
        # Make sure the mtime of both the Python source and the Sphinx input
        # files generated by autosummary is greater at a precision of 1 second
        # during the following run than the Sphinx output produced in the
        # previous run.
        time.sleep(1)
        foo_py = open(os.path.join('src', 'gocept', 'example', 'foo.py'), 'w')
        foo_py.write('def some_function(): pass')
        foo_py.close()
        subprocess.call([bin_doc])
        self.assertIn('some_function',
                      self.content('build/doc/_api/gocept.example.foo.html'))
