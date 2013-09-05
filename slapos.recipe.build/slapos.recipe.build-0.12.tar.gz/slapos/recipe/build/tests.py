from zope.testing import doctest
from zope.testing import renormalizing

import os
import re
import shutil
import stat
import tempfile
import unittest
import zc.buildout.testing

optionflags = (doctest.ELLIPSIS | doctest.NORMALIZE_WHITESPACE)

GIT_REPOSITORY = 'http://git.erp5.org/repos/slapos.recipe.build.git'
BAD_GIT_REPOSITORY = 'http://git.erp5.org/repos/nowhere'
REVISION = '2566127'

def setUp(test):
  zc.buildout.testing.buildoutSetUp(test)
  zc.buildout.testing.install_develop('slapos.recipe.build', test)

class GitCloneNonInformativeTests(unittest.TestCase):

  def setUp(self):
    self.dir = os.path.realpath(tempfile.mkdtemp())
    self.parts_directory_path = os.path.join(self.dir, 'test_parts')

  def tearDown(self):
    shutil.rmtree(self.dir)
    for var in os.environ.keys():
      if var.startswith('SRB_'):
        del os.environ[var]

  def write_file(self, filename, contents, mode=stat.S_IREAD | stat.S_IWUSR):
    path = os.path.join(self.dir, filename)
    fh = open(path, 'w')
    fh.write(contents)
    fh.close()
    os.chmod(path, mode)
    return path

  def makeGitCloneRecipe(self, options):
    from slapos.recipe.gitclone import Recipe
    bo = {
        'buildout': {
            'parts-directory': self.parts_directory_path,
            'directory': self.dir,
         }
    }
    default_options = {
      'repository': GIT_REPOSITORY
      }
    default_options.update(**options)
    return Recipe(bo, 'test', default_options)

  def test_using_download_cache_if_git_fails(self):
    from slapos.recipe.gitclone import GIT_CLONE_ERROR_MESSAGE, \
        GIT_CLONE_CACHE_ERROR_MESSAGE
    recipe = self.makeGitCloneRecipe({"use-cache": "true",
                                      "repository": BAD_GIT_REPOSITORY})
    os.chdir(self.dir)
    try:
      recipe.install()
      # Should have raised before.
      self.assertTrue(False)
    except zc.buildout.UserError, e:
      self.assertEquals(e.message, GIT_CLONE_CACHE_ERROR_MESSAGE)

  def test_not_using_download_cache_if_forbidden(self):
    from slapos.recipe.gitclone import GIT_CLONE_ERROR_MESSAGE, \
        GIT_CLONE_ERROR_MESSAGE
    recipe = self.makeGitCloneRecipe({"repository": BAD_GIT_REPOSITORY})
    os.chdir(self.dir)
    try:
      recipe.install()
      # Should have raised before.
      self.assertTrue(False)
    except zc.buildout.UserError, e:
      self.assertEquals(e.message, GIT_CLONE_ERROR_MESSAGE)

  def test_cleanup_of_pyc_files(self):
    recipe = self.makeGitCloneRecipe({})
    recipe.install()
    git_repository_path = os.path.join(self.parts_directory_path, "test")
    self.assertTrue(os.path.exists(git_repository_path))
    bad_file_path = os.path.join(git_repository_path, "foo.pyc")
    bade_file = open(bad_file_path, 'w')
    bade_file.close()
    self.assertTrue(os.path.exists(bad_file_path))
    # install again and make sure pyc file is removed
    recipe.update()
    self.assertTrue(os.path.exists(git_repository_path))
    self.assertFalse(os.path.exists(bad_file_path), "pyc file not removed")

  def test_ignore_ssl_certificate(self, ignore_ssl_certificate=True):
    from slapos.recipe.gitclone import GIT_CLONE_ERROR_MESSAGE, \
        GIT_CLONE_CACHE_ERROR_MESSAGE
    import slapos.recipe.gitclone

    # Monkey patch check_call
    original_check_call = slapos.recipe.gitclone.check_call
    check_call_paramater_list = []
    def patch_check_call(*args, **kw):
      check_call_paramater_list.extend([args, kw])
      original_check_call(args[0])
    slapos.recipe.gitclone.check_call = patch_check_call

    bo = {
        'buildout': {
            'parts-directory': self.parts_directory_path,
            'directory': self.dir,
         }
    }
    options = {
      'repository': GIT_REPOSITORY,
      "ignore-ssl-certificate": str(ignore_ssl_certificate).lower(),
      "repository": GIT_REPOSITORY
    }
    recipe = slapos.recipe.gitclone.Recipe(bo, 'test', options)

    recipe.install()

    # Check git clone parameters
    if ignore_ssl_certificate:
      self.assertTrue("--config" in check_call_paramater_list[0][0])
      self.assertTrue("http.sslVerify=false" in check_call_paramater_list[0][0])
    else:
      self.assertTrue(not "--config" in check_call_paramater_list[0][0])
      self.assertTrue(not "http.sslVerify=false" in check_call_paramater_list[0][0])

    # Restore original check_call method
    slapos.recipe.gitclone.check_call = original_check_call

  def test_ignore_ssl_certificate_false(self):
    self.test_ignore_ssl_certificate(ignore_ssl_certificate=False)

def test_suite():
  suite = unittest.TestSuite((
      doctest.DocFileSuite(
          'README.rst',
          module_relative=False,
          setUp=setUp,
          tearDown=zc.buildout.testing.buildoutTearDown,
          optionflags=optionflags,
          checker=renormalizing.RENormalizing([
              zc.buildout.testing.normalize_path,
              (re.compile(r'http://localhost:\d+'), 'http://test.server'),
              # Clean up the variable hashed filenames to avoid spurious
              # test failures
              (re.compile(r'[a-f0-9]{32}'), ''),
              ]),
          ),
      unittest.makeSuite(GitCloneNonInformativeTests),
      ))
  return suite

if __name__ == '__main__':
  unittest.main(defaultTest='test_suite')
