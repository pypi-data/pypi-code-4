import logging
import os
import time
import sys
import unittest

from deployer.env.go import GoEnvironment

from .base import Base


# Takes roughly about 6m on core2 + ssd, mostly cloudinit time
@unittest.skipIf(
    (not bool(os.environ.get("TEST_ENDPOINT"))),
    "Test env must be defined: TEST_ENDPOINT")
class LiveEnvironmentTest(Base):

    def setUp(self):
        self.endpoint = os.environ.get("TEST_ENDPOINT")
        self.output = self.capture_logging(
            "deployer", log_file=sys.stderr, level=logging.DEBUG)
        self.env = GoEnvironment(
            os.environ.get("JUJU_ENV"), self.endpoint)
        self.env.connect()
        self.assertFalse(self.env.status().get('services'))
        # Destroy everything.. consistent baseline
        self.env.reset(terminate_machines=True, terminate_delay=240)

    def tearDown(self):
        self.env.reset(terminate_machines=True, terminate_delay=240)
        self.env.close()

    def test_env(self):
        status = self.env.status()
        self.env.deploy("test-blog", "cs:precise/wordpress")
        self.env.deploy("test-db", "cs:precise/mysql")
        self.env.add_relation("test-db", "test-blog")
        self.env.add_units('test-blog', 1)

        # Sleep cause juju core watches are eventually consistent (5s window)
        # and status rpc is broken (http://pad.lv/1203105)
        time.sleep(6)
        self.env.wait_for_units(timeout=800)
        status = self.env.status()

        services = ["test-blog", "test-db"]
        self.assertEqual(
            sorted(status['services'].keys()),
            services)
        for s in services:
            for k, u in status['services'][s]['units'].items():
                self.assertEqual(u['agent-state'], "started")
