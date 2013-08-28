__license__ = """
Copyright 2012 DISQUS
Copyright 2013 Parse.ly, Inc.

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
"""

import random
import logging
import mock
import sys
import time
import traceback
import threading
import Queue

from itertools import cycle, islice
from kazoo.testing import KazooTestCase
from threading import Event

from samsa.exceptions import NoAvailablePartitionsError
from samsa.test.integration import KafkaIntegrationTestCase, FasterKafkaIntegrationTestCase, polling_timeout
from samsa.test.case import TestCase
from samsa.cluster import Cluster
from samsa.config import ConsumerConfig
from samsa.consumer import Consumer
from samsa.topics import Topic
from samsa.partitions import Partition
from samsa.consumer.partitions import PartitionOwnerRegistry, OwnedPartition


logger = logging.getLogger(__name__)

class TestConsumerIntegration(FasterKafkaIntegrationTestCase):

    def setUp(self):
        super(TestConsumerIntegration, self).setUp()
        self.kafka = self.kafka_broker.client
        self.client.ensure_path('/brokers/topics') # can be slow to create

    def _test(self):
        if hasattr(self, 'get_topic'):
            topic = self.get_topic().name
        else:
            topic = 'testtopic'
        print 'producing for %s' % topic
        self.kafka.produce(topic, 0, ['hello', 'world'])

    def test_01(self):
        self._test()

    def test_02(self):
        self._test()

    def test_03(self):
        self._test()

    def test_04(self):
        self._test()

    def test_05(self):
        self._test()

    def test_06(self):
        self._test()

    def test_07(self):
        self._test()

    def test_08(self):
        self._test()

    def test_09(self):
        self._test()

    def test_10(self):
        self._test()

if __name__ == '__main__':
    import unittest
    unittest.main()
