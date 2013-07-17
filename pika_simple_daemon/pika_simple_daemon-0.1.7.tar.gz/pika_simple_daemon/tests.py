from pika.adapters.blocking_connection import BlockingChannel
from pika_simple_daemon import Queue, Daemon
import unittest
import mock
from mock import ANY
from pika.adapters import BlockingConnection

def listen_and_print(queue_name, connection_details, queue_options):

    callback = Queue.print_body
    daemon = Daemon(connection_details)
    daemon.add_handler(queue_name, callback, timeout=None, limit=None, finish_on_empty=True, finished_callback=None, queue_options=queue_options)

    daemon.run()

class QueueTest(unittest.TestCase):

    def setUp(self):
        self._queue = Queue()
        self._queue.connection = mock.Mock(BlockingConnection)
        self._queue.channel = mock.Mock(BlockingChannel)

    def test_declare_queue(self):

        queue_options = {"auto_delete":True}

        queue_name_1 = "testa"
        queue_name_2 = "testb"
        queue_name_3 = "testc"


        queue_name = self._queue.declare_queue(queue_name_1, queue_options)
        self._queue.channel.queue_declare.assert_called_once_with(queue=queue_name_1, **queue_options)

        print queue_name

        self.assertEqual(1, len(self._queue.declared_channels))

        queue_name = self._queue.declare_queue(queue_name_1, queue_options)
        self._queue.channel.queue_declare.assert_called_once_with(queue=queue_name_1, **queue_options)

        print queue_name

        self.assertEqual(1, len(self._queue.declared_channels))

        self._queue.declare_queue(queue_name_2, queue_options)
        self._queue.channel.queue_declare.assert_called_with(queue=queue_name_2, **queue_options)

        self.assertEqual(2, len(self._queue.declared_channels))

    def test_send(self):

        queue_options = {"auto_delete":True}
        queue_name = "testa"
        exchange = "test-ex"
        routing_key = "test-rk"
        body = "TestBody"

        self._queue.send(exchange, routing_key, body)
        self._queue.channel.basic_publish.assert_called_once_with(body=body, exchange='test-ex', routing_key='test-rk', properties=ANY)

class DaemonTest(unittest.TestCase):

    queue_params = {"host":"localhost"}

    def setUp(self):
        self._daemon = Daemon(self.queue_params)

    def test_add_handler(self):
        queue_name = 'testy'
        callback = test_callback

        self._daemon.add_handler(queue_name, callback)
        self.assertEqual(len(self._daemon._handlers), 1)


    def test_run_hits_receive(self):


        queue_name = 'testy'
        callback = test_callback

        mock_receive = mock.Mock()

        self._daemon.add_handler(queue_name, callback, limit=1, timeout=1)
        self._daemon._receive = mock_receive


        self._daemon.run()

        mock_receive.assert_called_once_with(
            finished_callback=None, exchange_name=None, queue_name='testy', callback=test_callback, finish_on_empty=False, limit=1, timeout=1, queue_options={}
        )

    def test_run_calls_queue_receive(self):

        queue_name = 'testy'
        callback = test_callback

        mock_queue = mock.Mock(Queue)

        self._daemon.add_handler(queue_name, callback, limit=1, timeout=1)
        self._daemon._queue_class = mock.Mock
        self._daemon._run_once = True
        self._daemon.run()

        mock_queue.receive.assert_called_once()



def test_callback(body, routing_key, exchange):
    assert routing_key == "test-rk"
    assert exchange == "test-ex"
    assert body == {
        'a':'b'
    }


if __name__ == "__main__":
    unittest.main()

