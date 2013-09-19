#coding:utf-8
import unittest

from workertier.backends.pool import ConnectionPool, Connection


class TestConnectionPool(ConnectionPool):
    def _create_connection(self):
        return Connection()


class ConnectionPoolTestCase(unittest.TestCase):
    def setUp(self):
        self.pool = TestConnectionPool()

    def test_create_connection(self):
        self.assertEqual(0, len(self.pool._pool))
        with self.pool._acquire_connection():
            pass
        self.assertEqual(1, len(self.pool._pool))

    def test_connection_lock(self):
        with self.pool._acquire_connection() as connection1:
            self.assert_(connection1.lock.locked())
            with self.pool._acquire_connection() as connection2:
                self.assertNotEqual(connection1, connection2)

        for connection in self.pool._pool:
            self.assert_(not connection.lock.locked())

    def test_connection_reuse(self):
        with self.pool._acquire_connection() as connection1:
            pass
        with self.pool._acquire_connection() as connection2:
            pass
        self.assertEqual(connection1, connection2)

    def test_broken_connections_cleanup(self):
        with self.pool._acquire_connection() as connection1:
            connection1.broken = True
        self.assertEqual(1, len(self.pool._pool))
        self.assertEqual([connection1], self.pool._pool)
        with self.pool._acquire_connection() as connection2:
            pass
        self.assertNotEqual(connection1, connection2)
        self.assertEqual(1, len(self.pool._pool))
        self.assertEqual([connection2], self.pool._pool)

    def test_raise_if_broken(self):
        with self.pool._acquire_connection() as connection:
            class DummyExc(Exception):
                pass
            def test():
                with connection.raise_if_broken(DummyExc):
                    connection.broken = True
            self.assertRaises(DummyExc, test)

