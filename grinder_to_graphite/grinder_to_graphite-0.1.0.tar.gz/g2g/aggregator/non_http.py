
# Copyright (C) 2011-2013, Travis Bear
# All rights reserved.
#
# This file is part of Grinder to Graphite.
#
# Grinder to Graphite is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Grinder to Graphite is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Grinder to Graphite; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA

import socket
import datetime
import time
import math
import logging as log

# 'spandex.mycompany.com' becomes 'spandex'
SIMPLE_HOSTNAME = socket.gethostname().split('.')[0]
ALL_TRANSACTIONS = "All_Transactions"
PFX_PERSEC_PASSED = "per_second.tx_passed"
PFX_PERSEC_FAILED = "per_second.tx_failed"
PFX_LATENCY_MEAN = "latency.mean_time"
PFX_LATENCY_PERCENTILE = "latency.percentile"
PFX_RTG = "latency.group"


class NonHTTPAggregator(object):
    """
    (Non-Http Tests)

    <tx name>
        per_second
            tx_passed
            tx_failed
        latency
            mean_time
            percentile
                <specific percentiles defined in config>
            group
                <response time groups defined in config>
    """

    def __init__(self, start_timestamp, config):
        self.config = config
        self.graphite_prefix = self._get_graphite_prefix()
        # generate time group names
        self.time_group_milliseconds = self._get_time_group_ms()
        self.time_group_names = self._get_time_group_names()
        self.transaction_data = {}  # key: tx name, val: list of http/non-http data
        self._reset_data(start_timestamp)
        log.info("Initialized aggregator.  Reporting every %d seconds of data to %s" % (
            config.carbon_interval_seconds,
            config.carbon_host))
        log.info("Time groups: %s" % self.time_group_names)
        log.info("Data mapping: %s" % self.graphite_prefix)

    def _get_time_group_names(self):
        time_group_names = []
        if len(self.time_group_milliseconds) == 0:
            log.warn("No time groups specified.")
            return time_group_names
        time_group_names += ["under_%d_ms" % self.time_group_milliseconds[0]]
        if len(self.time_group_milliseconds) > 1:
            for i in range(1, len(self.time_group_milliseconds)):
                time_group_names += ["%d_to_%d_ms" % (
                    self.time_group_milliseconds[i - 1], self.time_group_milliseconds[i])]
        time_group_names += [
            "over_%d_ms" % self.time_group_milliseconds[len(self.time_group_milliseconds) - 1]]
        return time_group_names

    def _percentile(self, sorted_data, percent, key=lambda x: x):
        """
        based on this example:
        http://stackoverflow.com/questions/2374640/how-do-i-calculate-percentiles-with-python-numpy
        http://code.activestate.com/recipes/511478-finding-the-percentile-of-the-values/

        Find the percentile of a list of values.

        @parameter sorted_data - is a list of values. Note sorted_data MUST BE already sorted.
        @parameter percent - a float value from 0.0 to 1.0.
        @parameter key - optional key function to compute value from each element of sorted_data.

        @return - the percentile of the values
        """
        if not sorted_data:
            return None
        k = (len(sorted_data) - 1) * percent
        k_floor = math.floor(k)
        k_ceil = math.ceil(k)
        if k_floor == k_ceil:
            return key(sorted_data[int(k)])
        d0 = key(sorted_data[int(k_floor)]) * (k_ceil - k)
        d1 = key(sorted_data[int(k_ceil)]) * (k - k_floor)
        return d0 + d1

    def _get_graphite_prefix(self):
        gp = SIMPLE_HOSTNAME
        if self.config.carbon_prefix and self.config.carbon_prefix != "":
            gp = "%s.%s" % (self.config.carbon_prefix, gp)
        if self.config.carbon_suffix and self.config.carbon_suffix != "":
            gp = "%s.%s" % (gp, self.config.carbon_suffix)
        return gp

    def _get_time_group_ms(self):
        tgm = []
        if self.config.time_group_ms:
            return self.config.time_group_ms
        return tgm

    def _reset_data(self, timestamp):
        self.transaction_data = {}
        self.report_time = timestamp

    def _get_time_group(self, tx_time):
        for i in range(0, len(self.time_group_milliseconds)):
            if tx_time < self.time_group_milliseconds[i]:
                return self.time_group_names[i]
        return self.time_group_names[len(self.time_group_milliseconds)]

    def _get_new_time_group_dict(self):
        d = {}
        for name in self._get_time_group_names():
            d[name] = 0
        return d

    def _connect(self, socket, host, port):
        """
        Will try forever to get a connection to graphite
        """
        connected = False
        while not connected:
            try:
                socket.connect((host, port))
                connected = True
            except:
                sleep_time = self.config.follow_interval_seconds
                log.error("WARNING: failed to connect to Graphite at %s:%d.  Trying again in %d seconds" % (
                    host, port, sleep_time))
                time.sleep(sleep_time)

    def add_transaction(self, tx_name, tx_data):
        if tx_name not in self.transaction_data:
            self.transaction_data[tx_name] = []
        self.transaction_data[tx_name].append(tx_data)

    def _process_persec_metrics(self, metrics):
        """
        sets tps passed/failed by transaction name, and for ALL_TRANSACTIONS
        """
        all_tx_passed = 0.0
        all_tx_failed = 0.0
        for tx_name in self.transaction_data:
            passed = 0.0
            failed = 0.0
            for transaction in self.transaction_data[tx_name]:
                if transaction.errors > 0:
                    failed += transaction.errors
                    all_tx_failed += transaction.errors
                else:
                    passed += 1.0
                    all_tx_passed += 1.0
            graphite_path = "%s.%s.%s" % (self._get_graphite_prefix(), tx_name, PFX_PERSEC_PASSED)
            metrics[graphite_path] = passed / self.config.carbon_interval_seconds
            graphite_path = "%s.%s.%s" % (self._get_graphite_prefix(), tx_name, PFX_PERSEC_FAILED)
            metrics[graphite_path] = failed / self.config.carbon_interval_seconds
        graphite_path = "%s.%s.%s" % (self._get_graphite_prefix(), ALL_TRANSACTIONS, PFX_PERSEC_PASSED)
        metrics[graphite_path] = all_tx_passed / self.config.carbon_interval_seconds
        graphite_path = "%s.%s.%s" % (self._get_graphite_prefix(), ALL_TRANSACTIONS, PFX_PERSEC_FAILED)
        metrics[graphite_path] = all_tx_failed / self.config.carbon_interval_seconds

    def _process_latency_metrics(self, metrics):
        all_tx_total_time = 0.0
        all_tx_count = 0.0
        for tx_name in self.transaction_data:
            total_time = 0.0
            tx_count = 0.0
            for transaction in self.transaction_data[tx_name]:
                if transaction.errors > 0:
                    # grinder doesn't register time for failed transactions
                    continue
                total_time += transaction.time
                all_tx_total_time += transaction.time
                tx_count += 1
                all_tx_count += 1
            graphite_path = "%s.%s.%s" % (self._get_graphite_prefix(), tx_name, PFX_LATENCY_MEAN)
            if tx_count:
                metrics[graphite_path] = total_time / tx_count
        graphite_path = "%s.%s.%s" % (self._get_graphite_prefix(), ALL_TRANSACTIONS, PFX_LATENCY_MEAN)
        if all_tx_count:
            metrics[graphite_path] = all_tx_total_time / all_tx_count

    def __update_tx_percentile(self, tx_name, test_times, percentile, metrics):
        if percentile > 1.0 or percentile < 0:
            log.error("ERROR: illegal percentile '%f'.  Must be between 0.0 and 1.0" % percentile)
            return
        percentile_safe = "%s" % (percentile * 100)
        if percentile_safe.endswith(".0"):
            percentile_safe = percentile_safe[:len(percentile_safe) - 2]
        percentile_safe = percentile_safe.replace(".", "_")
        graphite_name = "%s.%s.%s.%s" % (self._get_graphite_prefix(),
                                         tx_name,
                                         PFX_LATENCY_PERCENTILE,
                                         percentile_safe)
        p_value = self._percentile(test_times, percentile)
        log.debug("Getting percentile %s for metric %s --> %s from list %s" % (
            percentile, tx_name, p_value, test_times))
        if p_value:
            metrics[graphite_name] = p_value

    def _process_percentile_metrics(self, metrics):
        # creates a duplicate list of all transaction times
        if not self.config.response_time_percentiles:
            log.info("No percentiles defined in config, skipping")
            return
        # calculate for "all transactions"
        all_test_times = []
        for tx_name in self.transaction_data:
            log.debug("processing percentile for tx name %s" % tx_name)
            test_times = []
            for test in self.transaction_data[tx_name]:
                if test.errors > 0:
                    continue
                all_test_times.append(test.time)
                test_times.append(test.time)
            test_times.sort()
            for percentile in self.config.response_time_percentiles:
                self.__update_tx_percentile(tx_name, test_times, percentile, metrics)
        all_test_times.sort()
        for percentile in self.config.response_time_percentiles:
            self.__update_tx_percentile(ALL_TRANSACTIONS, all_test_times, percentile, metrics)

    def _process_rtg_metrics(self, metrics):
        if not self.config.time_group_ms:
            log.debug("No time groups defined; time group processing skipped")
            return
        all_passed = 0.0
        all_tx_time_group_totals = self._get_new_time_group_dict()
        for tx_name in self.transaction_data:
            time_group_totals = self._get_new_time_group_dict()
            passed = 0.0
            for test in self.transaction_data[tx_name]:
                if test.errors > 0:
                    continue
                passed += 1.0
                all_passed += 1.0
                time_group_name = self._get_time_group(test.time)
                time_group_totals[time_group_name] += 1.0
                all_tx_time_group_totals[time_group_name] += 1.0
            for tg_name in self._get_time_group_names():
                graphite_name = "%s.%s.%s.%s" % (self._get_graphite_prefix(),
                                                 tx_name,
                                                 PFX_RTG,
                                                 tg_name)
                if passed:
                    metrics[graphite_name] = time_group_totals[tg_name] / passed
        for tg_name in self._get_time_group_names():
            graphite_name = "%s.%s.%s.%s" % (self._get_graphite_prefix(),
                                             ALL_TRANSACTIONS,
                                             PFX_RTG,
                                             tg_name)
            metrics[graphite_name] = all_tx_time_group_totals[tg_name] / all_passed

    def report_to_graphite(self):
        metrics = {}  # key: graphite path, value: metric value
        self._process_persec_metrics(metrics)
        self._process_latency_metrics(metrics)
        self._process_percentile_metrics(metrics)
        self._process_rtg_metrics(metrics)
        carbon_host = self.config.carbon_host
        carbon_port = self.config.carbon_port
        dt = datetime.datetime.fromtimestamp(self.report_time)
        log.info("Reporting to graphite (%s:%d) at %d (%s)" % (carbon_host, carbon_port, self.report_time, dt))
        graphite = socket.socket()
        self._connect(graphite, carbon_host, carbon_port)
        for metric_name in metrics:
            graphite.sendall("%s %f %d\n" % (metric_name, metrics[metric_name], self.report_time))
        # clean up
        graphite.close()
        self._reset_data(self.report_time + self.config.carbon_interval_seconds)


class HTTPAggregator(NonHTTPAggregator):
    def _process_persec_metrics(self, metrics):
        NonHTTPAggregator._process_persec_metrics(self, metrics)
        # TODO:

    def _process_latency_metrics(self, metrics):
        NonHTTPAggregator._process_latency_metrics(self, metrics)
        # TODO:

    def _process_percentile_metrics(self, metrics):
        NonHTTPAggregator._process_percentile_metrics(self, metrics)
        # TODO:

    def _process_rtg_metrics(self, metrics):
        NonHTTPAggregator._process_rtg_metrics(self, metrics)
        # TODO
