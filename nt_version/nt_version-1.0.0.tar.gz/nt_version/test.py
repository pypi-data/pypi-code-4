import unittest
import mox
import sys

import nt_version


class VersionReporterTestCase(unittest.TestCase):
    def setUp(self):
        super(VersionReporterTestCase, self).setUp()
        self.mox = mox.Mox()

    def tearDown(self):
        self.mox.VerifyAll()
        self.mox.UnsetStubs()
        super(VersionReporterTestCase, self).tearDown()

    def test_get_version_correct(self):
        """
        Make sure get version string from {project}.nt_version.version
        """
        expected_version = 'x.x.x'
        expected_project = 'snsd'

        project = self.mox.CreateMockAnything()
        project.nt_version = self.mox.CreateMockAnything()
        project.nt_version.version = expected_version
        self.mox.ReplayAll()

        sys.modules[expected_project] = project
        sys.modules['%s.nt_version' % expected_project] = project.nt_version

        self.assertEqual(expected_version,
                         nt_version._get_version(expected_project))
