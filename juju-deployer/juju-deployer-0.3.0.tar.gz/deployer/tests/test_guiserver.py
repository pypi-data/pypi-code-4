"""Tests for the GUI server bundles deployment support."""

import argparse
from contextlib import contextmanager
import os
import shutil
import tempfile
import unittest

import mock
import yaml

from deployer import (
    cli,
    guiserver,
)
from deployer.deployment import Deployment


class DeployerFunctionsTestMixin(object):
    """Base set up for the functions that make use of the juju-deployer."""

    apiurl = 'wss://api.example.com:17070'
    password = 'Secret!'
    name = 'mybundle'
    bundle = yaml.safe_load("""
      services:
        wordpress:
          charm: "cs:precise/wordpress-20"
          num_units: 1
          options:
            debug: "no"
            engine: nginx
            tuning: single
          annotations:
            "gui-x": "425.347"
            "gui-y": "414.547"
        mysql:
          charm: "cs:precise/mysql-28"
          num_units: 2
          constraints:
            arch: i386
            cpu-cores: 4
          annotations:
            "gui-x": "494.347"
            "gui-y": "164.547"
      relations:
        - - "mysql:db"
          - "wordpress:db"
      series: precise
    """)

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
    options = cli.setup_parser().parse_args([])

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

    def cleanup_series_path(self):
        """Remove the series path created by the Deployment object."""
        if os.path.isdir('precise'):
            os.rmdir('precise')

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

    @mock.patch('time.sleep')
    def test_importer_behavior(self, mock_sleep, mock_environment):
        # The importer executes the expected environment calls.
        self.addCleanup(self.cleanup_series_path)
        with self.patch_juju_home():
            self.import_bundle()
        mock_sleep.assert_has_calls([mock.call(5.1), mock.call(60)])
        # If any of the calls below fails, then we have to change the
        # signatures of deployer.guiserver.GUIEnvironment methods.
        mock_environment.assert_called_once_with(self.apiurl, self.password)
        mock_environment().assert_has_calls([
            mock.call.connect(),
            mock.call.status(),
            mock.call.deploy(
                'mysql', 'cs:precise/mysql-28', '', None,
                {'arch': 'i386', 'cpu-cores': 4}, 2, None),
            mock.call.set_annotation(
                'mysql', {'gui-y': '164.547', 'gui-x': '494.347'}),
            mock.call.deploy(
                'wordpress', 'cs:precise/wordpress-20', '',
                {'debug': 'no', 'engine': 'nginx', 'tuning': 'single'},
                None, 1, None),
            mock.call.set_annotation(
                'wordpress', {'gui-y': '414.547', 'gui-x': '425.347'}),
            mock.call.add_units('mysql', 2),
            mock.call.add_units('wordpress', 1),
            mock.call.add_relation('mysql:db', 'wordpress:db'),
            mock.call.close(),
        ], any_order=True)

    def test_options(self, mock_environment):
        # Ensure the default options are sane for us.
        expected = argparse.Namespace(
            bootstrap=False,
            branch_only=False,
            configs=None,
            debug=False,
            deploy_delay=0,
            deployment=None,
            description=False,
            destroy_services=False,
            diff=False,
            find_service=None,
            juju_env=os.environ.get("JUJU_ENV"),
            list_deploys=False,
            no_local_mods=True,
            overrides=None,
            rel_wait=60,
            retry_count=0,
            terminate_machines=False,
            timeout=2700,
            update_charms=False,
            verbose=False,
            watch=False)
        self.assertEqual(expected, self.options)
