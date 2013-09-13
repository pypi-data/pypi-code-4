"""Tests for the GUI server bundles deployment support."""

from contextlib import contextmanager
import os
import shutil
import tempfile
import unittest

import mock

from deployer import guiserver
from deployer.deployment import Deployment


class DeployerFunctionsTestMixin(object):
    """Base set up for the functions that make use of the juju-deployer."""

    apiurl = 'wss://api.example.com:17070'
    password = 'Secret!'
    name = 'mybundle'
    bundle = {'services': {'wordpress': {}, 'mysql': {}}}

    def check_environment_life(self, mock_environment):
        """Check the calls executed on the given mock environment.

        Ensure that, in order to retrieve the list of currently deployed
        services, the environment is instantiated, connected, env.status is
        called and then the connection is closed.
        """
        mock_environment.assert_called_once_with(self.apiurl, self.password)
        mock_env_instance = mock_environment()
        mock_env_instance.connect.assert_called_once_with()
        mock_env_instance.status.assert_called_once_with()
        mock_env_instance.close.assert_called_once_with()

    @contextmanager
    def assert_overlapping_services(self, mock_environment):
        """Ensure a ValueError is raised in the context manager block.

        The given mock environment object is set up so that its status
        simulates an existing service. The name of this service overlaps with
        the name of one of the services in the bundle.
        """
        mock_env_instance = mock_environment()
        mock_env_instance.status.return_value = {'services': {'mysql': {}}}
        # Ensure a ValueError is raised by the code in the context block.
        with self.assertRaises(ValueError) as context_manager:
            yield
        # The error reflects the overlapping service name.
        error = str(context_manager.exception)
        self.assertEqual('service(s) already in the environment: mysql', error)
        # Even if an error occurs, the environment connection is closed.
        mock_env_instance.close.assert_called_once_with()


@mock.patch('deployer.guiserver.GUIEnvironment')
class TestValidate(DeployerFunctionsTestMixin, unittest.TestCase):

    def test_validation(self, mock_environment):
        # The validation is correctly run.
        guiserver.validate(self.apiurl, self.password, self.bundle)
        # The environment is correctly instantiated and used.
        self.check_environment_life(mock_environment)

    def test_overlapping_services(self, mock_environment):
        # The validation fails if the bundle includes a service name already
        # present in the Juju environment.
        with self.assert_overlapping_services(mock_environment):
            guiserver.validate(self.apiurl, self.password, self.bundle)


@mock.patch('deployer.guiserver.GUIEnvironment')
class TestImportBundle(DeployerFunctionsTestMixin, unittest.TestCase):

    # The options attribute simulates the options passed to the Importer.
    options = 'mock options'

    @contextmanager
    def patch_juju_home(self):
        """Patch the value used by the bundle importer as Juju home."""
        base_dir = tempfile.mkdtemp()
        self.addCleanup(shutil.rmtree, base_dir)
        juju_home = os.path.join(base_dir, 'juju-home')
        with mock.patch('deployer.guiserver.JUJU_HOME', juju_home):
            try:
                yield juju_home
            finally:
                del os.environ['JUJU_HOME']

    def import_bundle(self):
        """Call the import_bundle function."""
        guiserver.import_bundle(
            self.apiurl, self.password, self.name, self.bundle, self.options)

    @mock.patch('deployer.guiserver.Importer')
    def test_importing_bundle(self, mock_importer, mock_environment):
        # The juju-deployer importer is correctly set up and run.
        with self.patch_juju_home():
            self.import_bundle()
        # The environment is correctly instantiated and used.
        self.check_environment_life(mock_environment)
        # The importer is correctly instantiated.
        self.assertEqual(1, mock_importer.call_count)
        importer_args = mock_importer.call_args[0]
        self.assertEqual(3, len(importer_args))
        env, deployment, options = importer_args
        # The first argument passed to the importer is the environment.
        self.assertIs(mock_environment(), env)
        # The second argument is the deployment object.
        self.assertIsInstance(deployment, Deployment)
        self.assertEqual(self.name, deployment.name)
        self.assertEqual(self.bundle, deployment.data)
        # The third and last argument is the options object.
        self.assertIs(self.options, options)
        # The importer is started.
        mock_importer().run.assert_called_once_with()

    def test_overlapping_services(self, mock_environment):
        # The import fails if the bundle includes a service name already
        # present in the Juju environment.
        with self.assert_overlapping_services(mock_environment):
            with self.patch_juju_home():
                self.import_bundle()

    @mock.patch('deployer.guiserver.Importer')
    def test_juju_home(self, mock_importer, mock_environment):
        # A customized Juju home is created and used during the import process.
        with self.patch_juju_home() as juju_home:
            assert not os.path.isdir(juju_home), 'directory should not exist'
            # Ensure JUJU_HOME is included in the context when the Importer
            # instance is run.
            run = lambda: self.assertEqual(juju_home, os.getenv('JUJU_HOME'))
            mock_importer().run = run
            self.import_bundle()
        # The JUJU_HOME directory has been created.
        self.assertTrue(os.path.isdir(juju_home))
