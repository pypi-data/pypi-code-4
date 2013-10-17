# -*- coding: utf-8 -*-

import time
import uuid

from mock import Mock, patch
from nose.tools import *

from bkyototycoon.client import KyotoTycoonConnection


class TestKyotoTycoonConnection(object):
    def test_constructor_lazy_connection(self):
        connection = KyotoTycoonConnection(lazy=True)

        ok_(not connection.is_connected())
        connection.open()
        ok_(connection.is_connected())

    def test_open_and_close(self):
        connection = KyotoTycoonConnection()

        ok_(connection.is_connected())
        connection.close()
        ok_(not connection.is_connected())

    @patch('socket.create_connection')
    def test_open_socket_timeout(self, mock_create_connection):
        mock_socket_ins = Mock()
        mock_create_connection.return_value = mock_socket_ins
        KyotoTycoonConnection(timeout=5.0)

        mock_socket_ins.settimeout.assert_called_once_with(5.0)

    def test_get_bulk(self):
        connection = KyotoTycoonConnection()
        data = {}
        for n in range(3):
            data[uuid.uuid1().hex] = n

        eq_({}, connection.get_bulk(data.keys()))

        connection.set_bulk(data)

        eq_(data, connection.get_bulk(data.keys()))
        eq_(data, connection.get_bulk(data.keys() + ['dummy_key']))

    def test_set_bulk(self):
        connection = KyotoTycoonConnection()
        data = {}
        for n in range(3):
            data[uuid.uuid1().hex] = n

        eq_(3, connection.set_bulk(data))
        eq_(data, connection.get_bulk(data.keys()))

    def test_set_bulk_async(self):
        connection = KyotoTycoonConnection()
        data = {uuid.uuid1().hex: 1}

        eq_(None, connection.set_bulk(data, async=True))

        time.sleep(0.3)
        eq_(data, connection.get_bulk(data.keys()))

    def test_set_bulk_lifetime(self):
        connection = KyotoTycoonConnection()
        data = {uuid.uuid1().hex: 1}

        eq_(1, connection.set_bulk(data, lifetime=0.1))

        time.sleep(1)
        eq_({}, connection.get_bulk(data.keys()))

    def test_remove_bulk(self):
        connection = KyotoTycoonConnection()
        data = {}
        for n in range(3):
            data[uuid.uuid1().hex] = n

        eq_(3, connection.set_bulk(data))
        eq_(data, connection.get_bulk(data.keys()))

        connection.remove_bulk(data.keys()[1:])
        eq_(data.items()[0:1], connection.get_bulk(data.keys()).items())

    def test_remove_bulk_async(self):
        connection = KyotoTycoonConnection()
        data = {uuid.uuid1().hex: 1}

        connection.set_bulk(data)
        eq_(data, connection.get_bulk(data.keys()))

        eq_(None, connection.remove_bulk(data.keys(), async=True))

        time.sleep(1)
        eq_({}, connection.get_bulk(data.keys()))
