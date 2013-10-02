import unittest
import os
from g2g.aggregator.non_http import NonHTTPAggregator, ALL_TRANSACTIONS
from g2g import g2g_config
from g2g.logtype.grinder.transaction import NonHTTPTest
from g2g.logtype.grinder import column_map
import datetime
import socket
import logging as log

SIMPLE_HOSTNAME = socket.gethostname().split('.')[0]
DEFAULT_RESPONSE_TIME = 175.0


def get_non_http_test(response_time=DEFAULT_RESPONSE_TIME, passed=True):
    line = "0, 0, 2, 1377884275587, %f, 0" % response_time
    words = line.split(", ")
    if not passed:
        words[column_map.ERRORS] = "1"
    return NonHTTPTest(words)


class TestAggregator(unittest.TestCase):

    def setUp(self):
        self.configfile = "aggregator.config"
        g2g_config.create_example_config_file(self.configfile)
        self.config = g2g_config.get_config([self.configfile])
        self.aggregator = NonHTTPAggregator(datetime.datetime.now, self.config)

    def tearDown(self):
        if os.path.exists(self.configfile):
            os.remove(self.configfile)

    def test_get_graphite_prefix(self):
        '''
        default config settings in [graphite]
        carbon_prefix = deleteme
        carbon_suffix = grinder
        '''

        # hostname only
        self.config.carbon_prefix = None
        self.config.carbon_suffix = None
        prefix = self.aggregator._get_graphite_prefix()
        expected = SIMPLE_HOSTNAME
        self.assertEqual(prefix, expected)

        # prefix only
        self.config.carbon_prefix = "pre"
        aggregator = NonHTTPAggregator(datetime.datetime.now, self.config)
        prefix = aggregator._get_graphite_prefix()
        expected = "pre." + SIMPLE_HOSTNAME
        self.assertEqual(prefix, expected)

        # prefix and suffix
        self.config.carbon_suffix = "post"
        aggregator = NonHTTPAggregator(datetime.datetime.now, self.config)
        prefix = aggregator._get_graphite_prefix()
        expected = "pre." + SIMPLE_HOSTNAME + ".post"
        self.assertEqual(prefix, expected)

        # suffix only
        self.config.carbon_prefix = None
        self.config.carbon_suffix = "rodent"
        aggregator = NonHTTPAggregator(datetime.datetime.now, self.config)
        prefix = aggregator._get_graphite_prefix()
        expected = SIMPLE_HOSTNAME + ".rodent"
        self.assertEqual(prefix, expected)

    def test_get_time_groups(self):
        time_groups = self.aggregator._get_time_group_ms()
        # time_group_milliseconds = 100, 200
        self.assertEqual(len(time_groups), 2)

    def test_get_time_group(self):
        # TODO: set these values based on configured time groups
        self.assertEqual(self.aggregator._get_time_group(10), "under_100_ms")
        self.assertEqual(self.aggregator._get_time_group(-10), "under_100_ms")
        self.assertEqual(self.aggregator._get_time_group(100), "100_to_200_ms")
        self.assertEqual(self.aggregator._get_time_group(150), "100_to_200_ms")
        self.assertEqual(self.aggregator._get_time_group(200), "over_200_ms")
        self.assertEqual(self.aggregator._get_time_group(2000), "over_200_ms")

    def test_get_time_group_names(self):
        # two thresholds defined ( default case )-- should return three items
        expected_groups = []
        expected_groups.append("under_%d_ms" % self.config.time_group_ms[0])
        expected_groups.append("%d_to_%d_ms" % (self.config.time_group_ms[0],
                                                self.config.time_group_ms[1]))
        expected_groups.append("over_%d_ms" % self.config.time_group_ms[1])
        self.assertEqual(expected_groups, self.aggregator._get_time_group_names())

        # no time thresholds defined -- should return an empty list
        self.config.time_group_ms = []
        aggregator = NonHTTPAggregator(datetime.datetime.now, self.config)
        self.assertEqual(aggregator._get_time_group_names(), [])

        # a single time threshold defined -- should return two items
        self.config.time_group_ms = [67]
        aggregator = NonHTTPAggregator(datetime.datetime.now, self.config)
        expected_groups = []
        expected_groups.append("under_%d_ms" % self.config.time_group_ms[0])
        expected_groups.append("over_%d_ms" % self.config.time_group_ms[0])
        self.assertEqual(expected_groups, aggregator._get_time_group_names())

    def test_add_transaction(self):
        self.assertFalse("test transaction" in self.aggregator.transaction_data)
        self.aggregator.add_transaction("test transaction", "test data")
        self.assertTrue("test transaction" in self.aggregator.transaction_data)
        self.assertEqual(len(self.aggregator.transaction_data["test transaction"]), 1)

    def test_process_persec_non_http(self):
        """
        Default reporting interval is 10 seconds.  Thus, these transactions:
            tx 1: 7 passed, 3 failed
            tx 2: 9 passed, 1 failed

        should produce:
            tx1 passed tps: 0.7
            tx1 failed tps: 0.3
            tx2 passed tps: 0.9
            tx2 failed tps: 0.1
            all tranactions passed/sec: 1.6
            all transactions failed/sec: 0.4
        """
        metrics = {}
        self.aggregator._reset_data(datetime.datetime.now())
        self.aggregator._process_persec_metrics(metrics)
        self.assertEqual(len(metrics), 2)
        tx1_name = "transaction_1"
        tx2_name = "transaction_2"
        self.aggregator._reset_data(datetime.datetime.now())
        # create 20 transactions, as described in docstring above
        for i in range(7):
            passed_tx = get_non_http_test()
            self.aggregator.add_transaction(tx1_name, passed_tx)
        for i in range(3):
            failed_tx = get_non_http_test(passed=False)
            self.aggregator.add_transaction(tx1_name, failed_tx)
        for i in range(9):
            passed_tx = get_non_http_test()
            self.aggregator.add_transaction(tx2_name, passed_tx)
        for i in range(1):
            failed_tx = get_non_http_test(passed=False)
            self.aggregator.add_transaction(tx2_name, failed_tx)
        self.aggregator._process_persec_metrics(metrics)
        self.assertEqual(len(metrics), 6)
        passed_name = "%s.%s.per_second.tx_passed" % (self.aggregator._get_graphite_prefix(), tx1_name)
        self.assertTrue(passed_name in metrics)
        self.assertEqual(metrics[passed_name], 0.7)
        failed_name = "%s.%s.per_second.tx_failed" % (self.aggregator._get_graphite_prefix(), tx2_name)
        self.assertEqual(metrics[failed_name], 0.1)
        all_passed_name = "%s.%s.per_second.tx_passed" % (self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertTrue(all_passed_name in metrics)
        self.assertEqual(metrics[all_passed_name], 1.6)

    def test_process_latency_non_http(self):
        """
        This data:
            tx1 times: [2.0, 3.0, 4.0, 5.0]  (4)
            tx1 failed: (3)
            tx2 times: [6.0, 7.0]
            tx2 failed: (1)
        Should result in these statistics:
            tx1 time: 3.5
            tx2 time: 6.5
            all tx time: 4.5
        """
        metrics = {}
        self.aggregator._reset_data(datetime.datetime.now())
        self.aggregator._process_latency_metrics(metrics)
        self.assertEqual(len(metrics), 0)
        # add the test data
        tx1_name = "timed_transaction_1"
        tx2_name = "timed_transaction_2"
        self.aggregator.add_transaction(tx1_name, get_non_http_test(response_time=2.0))
        self.aggregator.add_transaction(tx1_name, get_non_http_test(response_time=3.0))
        self.aggregator.add_transaction(tx1_name, get_non_http_test(response_time=4.0))
        self.aggregator.add_transaction(tx1_name, get_non_http_test(response_time=5.0))
        self.aggregator.add_transaction(tx2_name, get_non_http_test(response_time=6.0))
        self.aggregator.add_transaction(tx2_name, get_non_http_test(response_time=7.0))
        for i in range(3):
            self.aggregator.add_transaction(tx1_name, get_non_http_test(passed=False))
        self.aggregator.add_transaction(tx1_name, get_non_http_test(passed=False))
        # validate the test data has been processed correctly
        self.aggregator._process_latency_metrics(metrics)
        self.assertEqual(len(metrics), 3)
        l1_name = "%s.%s.latency.mean_time" % (self.aggregator._get_graphite_prefix(), tx1_name)
        l2_name = "%s.%s.latency.mean_time" % (self.aggregator._get_graphite_prefix(), tx2_name)
        l_all_name = "%s.%s.latency.mean_time" % (self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        log.warn("%s" % metrics.keys())
        self.assertEqual(metrics[l1_name], 3.5)  # see docstring
        self.assertEqual(metrics[l2_name], 6.5)
        self.assertEqual(metrics[l_all_name], 4.5)

    def test_process_percentile_metrics_not_enabled(self):
        metrics = {}
        tx1 = "disabled_percentiles"
        self.config.response_time_percentiles = []
        self.aggregator._reset_data(datetime.datetime.now())
        self.aggregator.add_transaction(tx1, get_non_http_test())
        self.aggregator._process_percentile_metrics(metrics)
        self.assertEqual(len(metrics), 0)

    def test_process_percentile_out_of_range(self):
        # percentile must range between 0.0 and 1.0
        metrics = {}
        self.config.response_time_percentiles = [-2.0, 1.5]
        self.aggregator._reset_data(datetime.datetime.now())
        self.aggregator._process_percentile_metrics(metrics)
        self.assertEqual(len(metrics), 0)

    def test_process_percentile_decimals_handled(self):
        metrics = {}
        tx_name = "perc_decimals"
        self.config.response_time_percentiles = [0.999, 0.5]
        self.aggregator._reset_data(datetime.datetime.now())
        self.aggregator.add_transaction(tx_name, get_non_http_test())
        self.aggregator._process_percentile_metrics(metrics)
        self.assertEqual(len(metrics), 4)
        graphite_name = "%s.%s.latency.percentile.99_9" % (self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertTrue(graphite_name in metrics)
        graphite_name = "%s.%s.latency.percentile.50" % (self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertTrue(graphite_name in metrics)

    def test_process_percentile_metrics(self):
        """
        Default config looks at 50th, 95th, 99th percentile
            tx1: 1-100
                50th: 50.5
                95th: 95.05
                99th: 99.01
            tx2: 101-200
                50th: 150.5
                95th: 190.05
                99th: 199.01
            all:
                50th: 100.5
                95th: 190.05
                99th: 198.01
        """
        metrics = {}
        self.aggregator._reset_data(datetime.datetime.now())
        self.aggregator._process_percentile_metrics(metrics)
        self.assertEqual(len(metrics), 0)
        tx1 = "perc_test1"
        for i in range(100):
            self.aggregator.add_transaction(tx1, get_non_http_test(float(i + 1)))
        tx2 = "perc_test2"
        for i in range(100):
            self.aggregator.add_transaction(tx2, get_non_http_test(float(i + 101)))
        self.aggregator._process_percentile_metrics(metrics)
        self.assertEqual(len(metrics), 9)
        graphite_name = "%s.%s.latency.percentile.50" % (self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertEqual(metrics[graphite_name], 100.5)
        graphite_name = "%s.%s.latency.percentile.95" % (self.aggregator._get_graphite_prefix(), tx1)
        self.assertEqual(metrics[graphite_name], 95.05)
        graphite_name = "%s.%s.latency.percentile.99" % (self.aggregator._get_graphite_prefix(), tx2)
        self.assertEqual(metrics[graphite_name], 199.01)

    def test_process_time_groups_not_enabled(self):
        metrics = {}
        tx1 = "disabled_percentiles"
        self.config.time_group_ms = []
        self.aggregator._reset_data(datetime.datetime.now())
        self.aggregator.add_transaction(tx1, get_non_http_test())
        self.aggregator._process_rtg_metrics(metrics)
        self.assertEqual(len(metrics), 0)

    def test_process_time_groups(self):
        """
        Default response time groups: 100 ms, 200 ms
        Test Data
            test 1
                50 ms : 7 (0.7 under 100 ms)
                150 ms: 3 (0.3 100 - 200 ms)
                250 ms: 0 (0.0 over  200 ms)
            test 2
                80 ms : 5 (0.5 under 100 ms)
                180 ms: 4 (0.4 100 - 200 ms)
                300 ms: 1 (0.1 over  200 ms)
            all transactions:
                under 100: 0.60
                100-200  : 0.35
                over 200 : 0.05
        """
        metrics = {}
        self.aggregator._reset_data(datetime.datetime.now())
        tx1 = "rtg1"
        tx2 = "rtg2"
        for i in range(7):
            self.aggregator.add_transaction(tx1, get_non_http_test(response_time=50))
        for i in range(3):
            self.aggregator.add_transaction(tx1, get_non_http_test(response_time=150))
        for i in range(0):
            self.aggregator.add_transaction(tx1, get_non_http_test(response_time=250))
        for i in range(5):
            self.aggregator.add_transaction(tx2, get_non_http_test(response_time=80))
        for i in range(4):
            self.aggregator.add_transaction(tx2, get_non_http_test(response_time=180))
        for i in range(1):
            self.aggregator.add_transaction(tx2, get_non_http_test(response_time=300))
        self.aggregator._process_rtg_metrics(metrics)
        self.assertEqual(len(metrics), 9)
        gp_name = "%s.%s.latency.group.under_100_ms" % (self.aggregator._get_graphite_prefix(), tx1)
        self.assertEqual(metrics[gp_name], 0.7)
        gp_name = "%s.%s.latency.group.100_to_200_ms" % (self.aggregator._get_graphite_prefix(), tx1)
        self.assertEqual(metrics[gp_name], 0.3)
        gp_name = "%s.%s.latency.group.over_200_ms" % (self.aggregator._get_graphite_prefix(), tx1)
        self.assertEqual(metrics[gp_name], 0.0)

        gp_name = "%s.%s.latency.group.under_100_ms" % (self.aggregator._get_graphite_prefix(), tx2)
        self.assertEqual(metrics[gp_name], 0.5)
        gp_name = "%s.%s.latency.group.100_to_200_ms" % (self.aggregator._get_graphite_prefix(), tx2)
        self.assertEqual(metrics[gp_name], 0.4)
        gp_name = "%s.%s.latency.group.over_200_ms" % (self.aggregator._get_graphite_prefix(), tx2)
        self.assertEqual(metrics[gp_name], 0.1)

        gp_name = "%s.%s.latency.group.under_100_ms" % (self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertEqual(metrics[gp_name], 0.6)
        gp_name = "%s.%s.latency.group.100_to_200_ms" % (self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertEqual(metrics[gp_name], 0.35)
        gp_name = "%s.%s.latency.group.over_200_ms" % (self.aggregator._get_graphite_prefix(), ALL_TRANSACTIONS)
        self.assertEqual(metrics[gp_name], 0.05)

    def test_get_new_time_group_dict(self):
        default_dict = self.aggregator._get_new_time_group_dict()
        self.assertEqual(len(default_dict), 3)
        self.assertEqual(default_dict[default_dict.keys()[1]], 0)
        self.config.time_group_ms = []
        aggregator = NonHTTPAggregator(datetime.datetime.now(), self.config)
        default_dict = aggregator._get_new_time_group_dict()
        self.assertEqual(len(default_dict), 0)
