"""Tests for the GUIEnvironment."""

import unittest

import mock

from deployer.env.gui import GUIEnvironment


@mock.patch('deployer.env.go.EnvironmentClient')
class TestGUIEnvironment(unittest.TestCase):

    endpoint = 'wss://api.example.com:17070'
    password = 'Secret!'

    def setUp(self):
        self.env = GUIEnvironment(self.endpoint, self.password)

    def test_connect(self, mock_client):
        # The environment uses the provided endpoint and password to connect
        # to the Juju API server.
        self.env.connect()
        mock_client.assert_called_once_with(self.endpoint)
        mock_client().login.assert_called_once_with(self.password)

    def test_multiple_connections(self, mock_client):
        # The environment does not attempt a second connection if it is already
        # connected to the API backend.
        self.env.connect()
        self.env.connect()
        self.assertEqual(1, mock_client.call_count)

    def test_close(self, mock_client):
        # The client attribute is set to None when the connection is closed.
        self.env.connect()
        self.env.close()
        self.assertIsNone(self.env.client)

    def test_deploy(self, mock_client):
        # The environment uses the API to deploy charms.
        self.env.connect()
        config = {'foo': 'bar'}
        constraints = {'cpu': 4}
        # Deploy a service: the last two arguments (force_machine and repo) are
        # ignored.
        self.env.deploy(
            'myservice', 'cs:precise/service-42', config=config,
            constraints=constraints, num_units=2, force_machine=1, repo='/tmp')
        mock_client().deploy.assert_called_once_with(
            'myservice', 'cs:precise/service-42', config=config,
            constraints=constraints, num_units=2)
