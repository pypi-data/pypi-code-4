# Copyright 2011 Canonical Ltd.  This software is licensed under the
# GNU Affero General Public License version 3 (see the file LICENSE).

"""Tests for the Rabbit fixture."""

__metaclass__ = type

import os.path
import socket
from textwrap import dedent

from amqplib import client_0_8 as amqp
from fixtures import EnvironmentVariableFixture
from rabbitfixture.server import (
    get_nodename_from_status,
    RabbitServer,
    RabbitServerEnvironment,
    RabbitServerResources,
    )
from testtools import TestCase
from testtools.testcase import gather_details


class TestRabbitFixture(TestCase):

    def setUp(self):
        super(TestRabbitFixture, self).setUp()
        # Rabbit needs to fully isolate itself: an existing per user
        # .erlang.cookie has to be ignored, and ditto bogus HOME if other
        # tests fail to cleanup.
        self.useFixture(EnvironmentVariableFixture('HOME', '/nonsense/value'))

    def test_start_check_shutdown(self):
        # The fixture correctly starts and stops RabbitMQ.
        with RabbitServer() as fixture:
            try:
                # We can connect.
                connect_arguments = {
                    "host": 'localhost:%s' % fixture.config.port,
                    "userid": "guest", "password": "guest",
                    "virtual_host": "/", "insist": False,
                    }
                amqp.Connection(**connect_arguments).close()
                # And get a log file.
                log = fixture.runner.getDetails()["server.log"]
                # Which shouldn't blow up on iteration.
                list(log.iter_text())
            except Exception:
                # self.useFixture() is not being used because we want to
                # handle the fixture's lifecycle, so we must also be
                # responsible for propagating fixture details.
                gather_details(fixture.getDetails(), self.getDetails())
                raise

        # The daemon should be closed now.
        self.assertRaises(socket.error, amqp.Connection, **connect_arguments)

    def test_config(self):
        # The configuration can be passed in.
        config = RabbitServerResources()
        fixture = self.useFixture(RabbitServer(config))
        self.assertIs(config, fixture.config)
        self.assertIs(config, fixture.runner.config)
        self.assertIs(config, fixture.runner.environment.config)


class TestRabbitServerResources(TestCase):

    def test_defaults(self):
        with RabbitServerResources() as resources:
            self.assertEqual("localhost", resources.hostname)
            self.assertIsInstance(resources.port, int)
            self.assertIsInstance(resources.homedir, (str, unicode))
            self.assertIsInstance(resources.mnesiadir, (str, unicode))
            self.assertIsInstance(resources.logfile, (str, unicode))
            self.assertIsInstance(resources.nodename, (str, unicode))

    def test_passed_to_init(self):
        args = dict(
            hostname="hostname", port=1234,
            homedir="homedir", mnesiadir="mnesiadir",
            logfile="logfile", nodename="nodename")
        resources = RabbitServerResources(**args)
        for i in range(2):
            with resources:
                for key, value in args.iteritems():
                    self.assertEqual(value, getattr(resources, key))

    def test_defaults_reallocated_after_teardown(self):
        seen_homedirs = set()
        resources = RabbitServerResources()
        for i in range(2):
            with resources:
                self.assertTrue(os.path.exists(resources.homedir))
                self.assertNotIn(resources.homedir, seen_homedirs)
                seen_homedirs.add(resources.homedir)

    def test_fq_nodename(self):
        resources = self.useFixture(RabbitServerResources(
            nodename="nibbles", hostname="127.0.0.1"))
        self.assertEqual("nibbles@127.0.0.1", resources.fq_nodename)


class TestRabbitServerEnvironment(TestCase):

    def test_setup(self):
        config = self.useFixture(RabbitServerResources(
            hostname="localhost", port=1234, homedir="rabbit/homedir",
            mnesiadir="rabbit/mnesiadir", logfile="rabbit/logfile",
            nodename="rabbit-nodename"))
        self.useFixture(RabbitServerEnvironment(config))
        expected = {
            "RABBITMQ_MNESIA_BASE": config.mnesiadir,
            "RABBITMQ_LOG_BASE": config.homedir,
            "RABBITMQ_NODE_IP_ADDRESS": socket.gethostbyname(config.hostname),
            "RABBITMQ_NODE_PORT": str(config.port),
            "RABBITMQ_NODENAME": config.fq_nodename,
            "RABBITMQ_PLUGINS_DIR": config.pluginsdir,
        }
        self.assertEqual(
            expected, {name: os.getenv(name) for name in expected})


class TestFunctions(TestCase):

    def test_get_nodename_from_status(self):
        example_status = dedent("""\
        Status of node tmpTAIyVi@obidos ...
        [{running_applications,
             [{rabbit_management,"RabbitMQ Management Console","0.0.0"},
              {webmachine,"webmachine","1.8.1"},
              {crypto,"CRYPTO version 1","1.6.3"},
              {amqp_client,"RabbitMQ AMQP Client","2.3.1"},
              {rabbit_management_agent,"RabbitMQ Management Agent","0.0.0"},
              {rabbit,"RabbitMQ","2.3.1"},
              {mnesia,"MNESIA  CXC 138 12","4.4.12"},
              {os_mon,"CPO  CXC 138 46","2.2.4"},
              {sasl,"SASL  CXC 138 11","2.1.8"},
              {rabbit_mochiweb,"RabbitMQ Mochiweb Embedding","0.0.0"},
              {stdlib,"ERTS  CXC 138 10","1.16.4"},
              {kernel,"ERTS  CXC 138 10","2.13.4"}]},
         {nodes,[{disc,[tmpTAIyVi@obidos]}]},
         {running_nodes,[tmpTAIyVi@obidos]}]
        """)
        self.assertEqual(
            "tmpTAIyVi@obidos",
            get_nodename_from_status(example_status))
