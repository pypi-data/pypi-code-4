from kforgeinstall.test import KForgeInstallTestCase
import unittest        
from kforgeinstall.cli import KForgeInstaller
import tempfile
import shutil
import os

import json, os

def suite():
    suites = [
#        unittest.makeSuite(TestKForgeInstallerBasics),
        unittest.makeSuite(TestKForgeInstallerCoreDev),
#        unittest.makeSuite(TestKForgeInstallerCoreStable),
#        unittest.makeSuite(TestKForgeInstallerDatabases),
#        unittest.makeSuite(TestKForgeInstallerServices),
    ]
    return unittest.TestSuite(suites)


class MockOptions(object): pass


class KForgeInstallerTestCase(KForgeInstallTestCase):

    def setUp(self):
        # Create tmp dir, and instantiate installer object.
        self.path = tempfile.mkdtemp(prefix='kforgeinstall-test', dir='/mnt/ram/')
        options = MockOptions()
        # Mock defaults.
        options.isVerbose = self.isVerbose
        options.isQuiet = False
        options.kforge_requirement_or_url = 'kforge'
        options.dm_requirement_or_url = ''
        options.withDav = False
        options.withTrac = False
        options.withMercurial = False
        options.withGit = False
        options.withSvn = False
        options.withAll = False
        options.withPython = ''
        self.installer = KForgeInstaller(self.path, options)

    def tearDown(self):
        if self.path:
            shutil.rmtree(self.path)


class TestKForgeInstallerBasics(KForgeInstallerTestCase):
 
    def test(self):
        # Sanity checks.
        self.assertEqual(os.path.join('a', 'b'), self.join('a', 'b'))
        self.assertPathExists('/dev/null')
        self.failUnlessRaises(Exception, self.assertPathExists, '/eettcc')
        self.assertPathMissing('/eettcc')
        self.failUnlessRaises(Exception, self.assertPathMissing, '/dev/null')

        #print "Test join() method."
        self.assertEqual(self.join('a', 'b'), self.installer.join('a', 'b'))

        #print "Test getBinPath() method."
        binPath = self.join(self.path, 'bin')
        self.failUnless(binPath)
        self.failUnless(self.path in binPath)
        self.assertEqual(binPath, self.installer.getBinPath())

        #print "Test getPythonBinPath() method."
        pythonBinPath = self.join(self.path, 'bin', 'python')
        self.failUnless(pythonBinPath)
        self.failUnless(self.path in pythonBinPath)
        self.assertEqual(pythonBinPath, self.installer.getPythonBinPath())

        #print "Test runCmd() method."
        self.installer.runCmd(['ls', '-l'])
        self.failUnlessRaises(Exception, self.installer.runCmd, ['lllls', '-l'])

        #print "Test createVirtualenv() method."
        self.assertPathMissing(pythonBinPath)
        self.installer.createVirtualenv()
        self.assertPathExists(pythonBinPath)
        self.installer.runCmd([pythonBinPath, '-V'])

        #print "Test canPythonImport() method."
        self.failUnless(self.installer.canPythonImport('os'))
        self.failIf(self.installer.canPythonImport('virtualenv'))

        #print "Test getPipBinPath() method."
        pipBinPath = self.join(self.path, 'bin', 'pip')
        self.failUnless(pipBinPath)
        self.failUnless(self.path in pipBinPath)
        self.assertEqual(pipBinPath, self.installer.getPipBinPath())

        #print "Test pipInstall() method."
        self.failIf(self.installer.canPythonImport('urllib3'))
        self.installer.pipInstall('urllib3')
        self.failUnless(self.installer.canPythonImport('urllib3'))
        self.failUnlessRaises(Exception, self.installer.pipInstall, 'urllib33333')


class KForgeInstallerCoreTestCase(KForgeInstallerTestCase):

    def setUp(self):
        super(KForgeInstallerCoreTestCase, self).setUp()
        # Create virtualenv.
        self.installer.createVirtualenv()

    def getVersion(self, level, system):
        v = json.loads(open(os.path.expanduser('~/.asfversions')).read())
        return v[level][system]

    
class TestKForgeInstallerCoreStable(KForgeInstallerCoreTestCase):

    def testInstallKForge(self):
        self.failIf(self.installer.canPythonImport('kforge'))
        self.installer.installKForge()
        self.failUnless(self.installer.canPythonImport('kforge'))
   
    def testInstallDomainModel(self): 
        self.failIf(self.installer.canPythonImport('dm'))
        self.installer.installDomainModel()
        self.failIf(self.installer.canPythonImport('dm'))
        dmUrl = 'http://appropriatesoftware.net/provide/docs/domainmodel-%s.tar.gz' % self.getVersion('stable', 'domainmodel')
        self.installer.options.dm_requirement_or_url = dmUrl
        self.installer.installDomainModel()
        self.failUnless(self.installer.canPythonImport('dm'))


class TestKForgeInstallerCoreDev(KForgeInstallerCoreTestCase):

    def testInstallKForgeDev(self):
        # Test the installer can install the development versions.
        # URLs need to be maintained as the latest development versions.
        kforgeUrl = 'http://appropriatesoftware.net/provide/docs/kforge-%s.tar.gz' % self.getVersion('development', 'kforge')
        dmUrl = 'http://appropriatesoftware.net/provide/docs/domainmodel-%s.tar.gz' % self.getVersion('development', 'domainmodel')
        self.failIf(self.installer.canPythonImport('kforge'))
        # Set path to development kforge distribution.
        self.installer.options.kforge_requirement_or_url = kforgeUrl
        # Check the installer fails (domainmodel distribution not yet set).
        self.failUnlessRaises(Exception, self.installer.installKForge)
        # Set path to development domainmodel distribution.
        self.installer.options.dm_requirement_or_url = dmUrl
        # Check the installer succeedes.
        self.installer.installKForge()
        self.failUnless(self.installer.canPythonImport('kforge'))
    

class TestKForgeInstallerDatabases(KForgeInstallerTestCase):

    def setUp(self):
        super(TestKForgeInstallerDatabases, self).setUp()
        self.installer.createVirtualenv()

    def testInstallPostgresql(self):
        #print "Test installMxDateTime."
        self.failIf(self.installer.canPythonImport('mx.DateTime'))
        self.installer.installMxDateTime()
        self.failUnless(self.installer.canPythonImport('mx.DateTime'))

        #print "Test installPsycopg2."
        self.failIf(self.installer.canPythonImport('psycopg2'))
        self.installer.installPsycopg2()
        self.failUnless(self.installer.canPythonImport('psycopg2'))

    def testInstallMysql(self):
        #print "Test installMysql."
        self.failIf(self.installer.canPythonImport('MySQLdb'))
        self.installer.installMysql()
        self.failUnless(self.installer.canPythonImport('MySQLdb'))


class TestKForgeInstallerServices(KForgeInstallerTestCase):

    def setUp(self):
        super(TestKForgeInstallerServices, self).setUp()
        self.installer.createVirtualenv()

    def testInstallDav(self):
        self.installer.options.withDav = True
        self.failIf(self.installer.canPythonImport('wsgidav'))
        self.installer.installServices()
        self.failUnless(self.installer.canPythonImport('wsgidav'))

    def testInstallTracGitHg(self):
        self.installer.options.withTrac = True
        self.installer.options.withGit = True
        self.installer.options.withMercurial = True
        self.installer.options.withSvn = True
        self.failIf(self.installer.canPythonImport('trac'))
        self.failIf(self.installer.canPythonImport('tracext.hg'))
        self.failIf(self.installer.canPythonImport('svn'))
        self.installer.installServices()
        self.failUnless(self.installer.canPythonImport('trac'))
        self.failUnless(self.installer.canPythonImport('tracext.hg'))
        self.failUnless(self.installer.canPythonImport('svn'))

    def testInstallMercurial(self):
        self.installer.options.withMercurial = True
        self.failIf(self.installer.canPythonImport('mercurial'))
        self.installer.installServices()
        self.failUnless(self.installer.canPythonImport('mercurial'))

    def testInstallSubversion(self):
        self.installer.options.withSvn = True
        self.failIf(self.installer.canPythonImport('svn'))
        self.failIf(self.installer.canPythonImport('wsgidav'))
        self.installer.installServices()
        self.failUnless(self.installer.canPythonImport('svn'))
        self.failUnless(self.installer.canPythonImport('wsgidav'))

    def testInstallTrac(self):
        self.installer.options.withTrac = True
        self.failIf(self.installer.canPythonImport('trac'))
        self.failIf(self.installer.canPythonImport('tracext.hg'))
        self.failIf(self.installer.canPythonImport('svn'))
        self.installer.installServices()
        self.failUnless(self.installer.canPythonImport('trac'))
        self.failIf(self.installer.canPythonImport('tracext.hg'))
        self.failIf(self.installer.canPythonImport('svn'))

    def testInstallAll(self):
        self.installer.options.withAll = True
        self.installer.installServices()
        self.failUnless(self.installer.canPythonImport('mercurial'))
        self.failUnless(self.installer.canPythonImport('wsgidav'))
        self.failUnless(self.installer.canPythonImport('trac'))
        self.failUnless(self.installer.canPythonImport('tracext.hg'))
        self.failUnless(self.installer.canPythonImport('svn'))


