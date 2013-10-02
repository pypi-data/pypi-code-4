import unittest
import os
from g2g.aggregator.non_http import ALL_TRANSACTIONS, NonHTTPAggregator
from g2g.aggregator.http import HTTPAggregator
from g2g import g2g_config
from g2g.logtype.grinder.transaction import HTTPTest
from g2g.logtype.grinder import column_map
from test_non_http_aggregator import DEFAULT_RESPONSE_TIME
import datetime
import socket
import logging as log
import random

SIMPLE_HOSTNAME = socket.gethostname().split('.')[0]
DEFAULT_PASSED = True
DEFAULT_RC = 200
DEFAULT_RESOLVE_HOST_TIME = 1.1
DEFAULT_CONNECT_TIME = 13.0
DEFAULT_FIRST_BYTE_TIME = 100.0
DEFAULT_NEW_CONNECTIONS = 1.0


def get_http_test(response_time=DEFAULT_RESPONSE_TIME,
                  passed=DEFAULT_PASSED,
                  rc=DEFAULT_RC,
                  new_connections=DEFAULT_NEW_CONNECTIONS,
                  length=random.randint(1000, 2000),
                  resolve_host=DEFAULT_RESOLVE_HOST_TIME,
                  establish_connection=DEFAULT_CONNECT_TIME,
                  first_byte=DEFAULT_FIRST_BYTE_TIME):
    line = "0, 0, 2, 1377884275587, %f, 0, 200, 132, 0, 0, 166, 359, 1" % response_time
    words = line.split(", ")
    if not passed:
        words[column_map.ERRORS] = "1"
    words[column_map.HTTP_RESPONSE_CODE] = "%s" % rc
    words[column_map.NEW_CONNECTIONS] = "%s" % new_connections
    words[column_map.HTTP_RESPONSE_LENGTH] = "%s" % length
    words[column_map.RESOLVE_HOST_TIME] = "%s" % resolve_host
    words[column_map.ESTABLISH_CONNECTION_TIME] = "%s" % establish_connection
    words[column_map.FIRST_BYTE_TIME] = "%s" % first_byte
    return HTTPTest(words)


class TestHttpAggregator(unittest.TestCase):

    def setUp(self):
        self.configfile = "aggregator.config"
        g2g_config.create_example_config_file(self.configfile)
        self.config = g2g_config.get_config([self.configfile])
        self.aggregator = HTTPAggregator(datetime.datetime.now, self.config)
        self.aggregator._reset_data(datetime.datetime.now())

    def tearDown(self):
        if os.path.exists(self.configfile):
            os.remove(self.configfile)

    def test_process_persec_bytes_downloaded(self):
        """
        Default reporting interval is 10 seconds.  Thus, these transactions:
            tx 1: 7 @ 1200, 3 @ 500
            tx 2: 8 @ 300, 2 @0 600

        should produce:
            tx1             : (8400 + 1500) / 10 == 990.0
            tx2             : (2400 + 1200) / 10 == 360.0
            all tranactions : (990 + 360)  == 1350.0
        """
        metrics = {}
        tx1_name = "bytes_1"
        tx2_name = "bytes_2"
        for i in range(7):
            default_tx = get_http_test(length=1200)  # passed, rc 200
            self.aggregator.add_transaction(tx1_name, default_tx)
        for i in range(3):
            not_found_tx = get_http_test(length=500)
            self.aggregator.add_transaction(tx1_name, not_found_tx)
        for i in range(8):
            default_tx = get_http_test(length=300)  # passed, rc 200
            self.aggregator.add_transaction(tx2_name, default_tx)
        for i in range(2):
            not_found_tx = get_http_test(length=600)
            self.aggregator.add_transaction(tx2_name, not_found_tx)
        self.aggregator._process_persec_metrics(metrics)
        # validate
        graphite_path = "%s.%s.per_second.bytes_downloaded" % (
            self.aggregator._get_graphite_prefix(), tx1_name)
        self.assertEqual(metrics[graphite_path], 990.0)
        graphite_path = "%s.%s.per_second.bytes_downloaded" % (
            self.aggregator._get_graphite_prefix(), tx2_name)
        self.assertEqual(metrics[graphite_path], 360.0)
        graphite_path = "%s.%s.per_second.bytes_downloaded" % (
            self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertEqual(metrics[graphite_path], 1350.0)

    def test_process_persec_new_connections(self):
        """
        Default reporting interval is 10 seconds.  Thus, these transactions:
            tx 1: 7@1, 3@0
            tx 2: 8@1, 2@0

        should produce:
            tx1             : 0.7
            tx2             : 0.8
            all tranactions : 1.5
        """
        metrics = {}
        tx1_name = "new_cxn_1"
        tx2_name = "new_cxn_2"
        for i in range(7):
            default_tx = get_http_test(new_connections=1)  # passed, rc 200
            self.aggregator.add_transaction(tx1_name, default_tx)
        for i in range(3):
            not_found_tx = get_http_test(new_connections=0)
            self.aggregator.add_transaction(tx1_name, not_found_tx)
        for i in range(8):
            default_tx = get_http_test(new_connections=1)  # passed, rc 200
            self.aggregator.add_transaction(tx2_name, default_tx)
        for i in range(2):
            not_found_tx = get_http_test(new_connections=0)
            self.aggregator.add_transaction(tx2_name, not_found_tx)
        self.aggregator._process_persec_metrics(metrics)
        # validate
        graphite_path = "%s.%s.per_second.new_connections" % (
            self.aggregator._get_graphite_prefix(), tx1_name)
        self.assertEqual(metrics[graphite_path], 0.7)
        graphite_path = "%s.%s.per_second.new_connections" % (
            self.aggregator._get_graphite_prefix(), tx2_name)
        self.assertEqual(metrics[graphite_path], 0.8)
        graphite_path = "%s.%s.per_second.new_connections" % (
            self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertEqual(metrics[graphite_path], 1.5)

    def test_process_persec_http_rc(self):
        """
        Default reporting interval is 10 seconds.  Thus, these transactions:
            tx 1: 6 rc_200, 3 rc_404, 1 rc_500 (failure)
            tx 2: 8 rc_200, 2 rc_302

        should produce:
            tx1
                passed tps: 0.9
                failed tps: 0.1
                rc_200/sec: 0.6
                rc_404/sec: 0.3
                rc_500/sec: 0.1
                new_connxs: 2.0
                bytes_down: > 1k
            tx2
                passed tps: 1.0
                failed tps: 0.0
                rc_200/sec: 0.8
                rc_302/sec: 0.2
                new_connxs: 2.0
                bytes_down: > 1k
            all tranactions
                passed/sec: 1.9
                failed/sec: 0.1
                new_connxs: 2.0
                bytes_down: > 1k
                rc_200/sec: 1.4
                rc_302/sec: 0.2
                rc_404/sec: 0.3
                rc_500/sec: 0.1
        """
        metrics = {}
        self.aggregator._process_persec_metrics(metrics)
        self.assertEqual(len(metrics), 4)
        tx1_name = "http_tx_1"
        tx2_name = "http_tx_2"
        self.aggregator._reset_data(datetime.datetime.now())
        # create 20 transactions, as described in docstring above
        for i in range(6):
            default_tx = get_http_test()  # passed, rc 200
            self.aggregator.add_transaction(tx1_name, default_tx)
        for i in range(3):
            not_found_tx = get_http_test(rc=404)  # passed, rc 404
            self.aggregator.add_transaction(tx1_name, not_found_tx)
        for i in range(1):
            failed_tx = get_http_test(passed=False, rc=500)  # failed, rc 500
            self.aggregator.add_transaction(tx1_name, failed_tx)
        for i in range(8):
            default_tx = get_http_test()
            self.aggregator.add_transaction(tx2_name, default_tx)
        for i in range(2):
            redirect_tx = get_http_test(rc=302)
            self.aggregator.add_transaction(tx2_name, redirect_tx)
        self.aggregator._process_persec_metrics(metrics)
        for m in sorted(metrics.keys()):
            log.debug((m, metrics[m]))
        self.assertEqual(len(metrics), 21)
        graphite_path = "%s.%s.per_second.http_status.rc_200" % (
            self.aggregator._get_graphite_prefix(), tx1_name)
        self.assertEqual(metrics[graphite_path], 0.6)
        graphite_path = "%s.%s.per_second.tx_passed" % (
            self.aggregator._get_graphite_prefix(), tx1_name)
        self.assertEqual(metrics[graphite_path], 0.9)
        graphite_path = "%s.%s.per_second.http_status.rc_302" % (
            self.aggregator._get_graphite_prefix(), tx2_name)
        self.assertEqual(metrics[graphite_path], 0.2)
        graphite_path = "%s.%s.per_second.http_status.rc_200" % (
            self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertEqual(metrics[graphite_path], 1.4)
        graphite_path = "%s.%s.per_second.tx_passed" % (
            self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertEqual(metrics[graphite_path], 1.9)

    def test_process_latency_some_new_1(self):
        """
        Default reporting interval is 10 seconds.  Thus, these transactions:

                       time   resolve   connect   1stbyte   new_conns
            tx 1:
                5)      175.0    1.1     13.0      100.0       1
                5)      225.0    ---     ----      200.0       0
            tx 2:
                6)      100.0    2.2     9.0       60          1
                4)      110.0    ---     ---       105.0       0

        should produce:
            tx1:         200.0   1.1    13.0      150.0
            tx2:         104.0   2.2    9.0       105.0
            all tx :     152.0   1.7    10.81...  114.0
        """
        metrics = {}
        tx1_name = "latency_tx_1"
        tx2_name = "latency_tx_2"
        self.aggregator._reset_data(datetime.datetime.now())
        # create 20 transactions, as described in docstring above
        for i in range(5):
            default_tx = get_http_test(response_time=175.0,
                                       establish_connection=13.0,
                                       first_byte=100.0,
                                       new_connections=1)
            self.aggregator.add_transaction(tx1_name, default_tx)
        for i in range(5):
            tx = get_http_test(response_time=225.0,
                               first_byte=200.0,
                               new_connections=0.0)
            self.aggregator.add_transaction(tx1_name, tx)
        for i in range(6):
            default_tx = get_http_test(response_time=100.0,
                                       resolve_host=2.2,
                                       establish_connection=9.0,
                                       first_byte=60.0,
                                       new_connections=1)
            self.aggregator.add_transaction(tx2_name, default_tx)
        for i in range(4):
            tx = get_http_test(response_time=104.0,
                               first_byte=200.0,
                               new_connections=0.0)
            self.aggregator.add_transaction(tx2_name, tx)
        self.aggregator._process_latency_metrics(metrics)
        for key in sorted(metrics):
            log.warn("%s: %s" % (key, metrics[key]))
        self.assertEqual(len(metrics), 12)
        graphite_path = "%s.%s.latency.http.first_byte.mean_time" % (
            self.aggregator._get_graphite_prefix(), tx1_name)
        self.assertEqual(metrics[graphite_path], 150.0)
        graphite_path = "%s.%s.latency.http.resolve_host.mean_time" % (
            self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertEqual(metrics[graphite_path], 1.7)
        # ... others as desired

    def test_process_latency_some_new_2(self):
        """
        Default reporting interval is 10 seconds.  Thus, these transactions:

                       time   resolve   connect   1stbyte   new_conns
            tx 1:
                5)      160.0    1.1     8.0       155.0       1
                5)      180.0    ---     ----      175.0       0
            tx 2:
                6)      104.0    ---     ---       100         0
                4)      120.0    ---     ---       105.0       0

        should produce:
            tx1:         170.0   1.1    8.0       165.0
            tx2:         110.4   ---    ---       105.0
            all tx :     120.0   1.1    8.0       121.5
        """
        metrics = {}
        tx1_name = "latency_tx_1"
        tx2_name = "latency_tx_2"
        self.aggregator._reset_data(datetime.datetime.now())
        # create 20 transactions, as described in docstring above
        for i in range(5):
            default_tx = get_http_test(response_time=160.0,
                                       establish_connection=8.0,
                                       first_byte=155.0,
                                       new_connections=1)
            self.aggregator.add_transaction(tx1_name, default_tx)
        for i in range(5):
            tx = get_http_test(response_time=180.0,
                               first_byte=175.0,
                               new_connections=0.0)
            self.aggregator.add_transaction(tx1_name, tx)
        for i in range(6):
            default_tx = get_http_test(response_time=104.0,
                                       first_byte=100.0,
                                       new_connections=0)
            self.aggregator.add_transaction(tx2_name, default_tx)
        for i in range(4):
            tx = get_http_test(response_time=120.0,
                               first_byte=105.0,
                               new_connections=0.0)
            self.aggregator.add_transaction(tx2_name, tx)
        self.aggregator._process_latency_metrics(metrics)
        for key in sorted(metrics):
            log.warn("%s: %s" % (key, metrics[key]))
        self.assertEqual(len(metrics), 10)
        graphite_path = "%s.%s.latency.http.first_byte.mean_time" % (
            self.aggregator._get_graphite_prefix(), tx1_name)
        self.assertEqual(metrics[graphite_path], 165.0)
        graphite_path = "%s.%s.latency.http.resolve_host.mean_time" % (
            self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertEqual(metrics[graphite_path], 1.1)
        # ... others as desired

    def test_process_latency_all_new(self):
        """
        Default reporting interval is 10 seconds.  Thus, these transactions:

                       time   resolve   connect   1stbyte   new_conns
            tx 1:
                5)      260.0    1.5     25.0      250.0       1
                5)      200.0    1.1     22.0      196.0       1
            tx 2:
                6)      100.0    1.0     17.0      90.0        1
                4)      110.0    1.2     20.0      105.0       1

        should produce:
            tx1:        230.0    1.3     23.5      223.0
            tx2:        104.0    1.08    18.2      96.0
            all tx :    167.0    1.19    20.85     159.5
        """
        pass
        # TODO:

    def test_process_latency_no_new(self):
        """
        Default reporting interval is 10 seconds.  Thus, these transactions:

                       time   resolve   connect   1stbyte   new_conns
            tx 1:
                5)      160.0    ---     ---       155.0       0
                5)      180.0    ---     ---       175.0       0
            tx 2:
                6)      104.0    ---     ---       100.0       0
                4)      120.0    ---     ---       105.0       0

        should produce:
            tx1:         170.0   ---    ---        165.0
            tx2:         110.4   ---    ---        102.0
            all tx :     140.2   ---    ---        133.5
        """
        metrics = {}
        tx1_name = "latency_tx_1"
        tx2_name = "latency_tx_2"
        self.aggregator._reset_data(datetime.datetime.now())
        # create 20 transactions, as described in docstring above
        for i in range(5):
            default_tx = get_http_test(response_time=160.0,
                                       first_byte=155.0,
                                       new_connections=0)
            self.aggregator.add_transaction(tx1_name, default_tx)
        for i in range(5):
            tx = get_http_test(response_time=180.0,
                               first_byte=175.0,
                               new_connections=0.0)
            self.aggregator.add_transaction(tx1_name, tx)
        for i in range(6):
            default_tx = get_http_test(response_time=104.0,
                                       first_byte=100.0,
                                       new_connections=0)
            self.aggregator.add_transaction(tx2_name, default_tx)
        for i in range(4):
            tx = get_http_test(response_time=120.0,
                               first_byte=105.0,
                               new_connections=0.0)
            self.aggregator.add_transaction(tx2_name, tx)
        self.aggregator._process_latency_metrics(metrics)
        for key in sorted(metrics):
            log.warn("%s: %s" % (key, metrics[key]))
        self.assertEqual(len(metrics), 6)
        graphite_path = "%s.%s.latency.http.first_byte.mean_time" % (
            self.aggregator._get_graphite_prefix(), tx1_name)
        self.assertEqual(metrics[graphite_path], 165.0)
        graphite_path = "%s.%s.latency.http.first_byte.mean_time" % (
            self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertEqual(metrics[graphite_path], 133.5)
        # ... others as desired
