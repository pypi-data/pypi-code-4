
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

import logging as log
from g2g.aggregator.non_http import ALL_TRANSACTIONS
from g2g.aggregator.non_http import NonHTTPAggregator

PFX_PERSEC_BYTES = "per_second.bytes_downloaded"
PFX_PERSEC_CONNECTIONS = "per_second.new_connections"
PFX_PERSEC_HTTP_RC = "per_second.http_status.rc_"
PFX_LATENCY_HTTP_RESOLVE_HOST = "latency.http.resolve_host.mean_time"
PFX_LATENCY_HTTP_EST_CONN = "latency.http.establish_connection.mean_time"
PFX_LATENCY_HTTP_FIRST_BYTE = "latency.http.first_byte.mean_time"


class HTTPAggregator(NonHTTPAggregator):
    """

    """
    def _process_persec_metrics(self, metrics):
        """
        <tx name>
        **  per_second
                bytes_downloaded
        **      tx_passed
        **      tx_failed
                new_connections
                http_status
                    rc_200
                    rc_302
                    rc_404
                    ...

        **  generated in superclass
        """
        NonHTTPAggregator._process_persec_metrics(self, metrics)
        all_bytes_downloaded = 0.0
        all_new_connections = 0.0
        all_status_codes = {}
        for tx_name in self.transaction_data:
            bytes_downloaded = 0.0
            new_connections = 0.0
            status_codes = {}
            for transaction in self.transaction_data[tx_name]:
                bytes_downloaded += transaction.http_response_length
                all_bytes_downloaded += transaction.http_response_length
                new_connections += transaction.new_connections
                all_new_connections += transaction.new_connections
                if not transaction.http_rc in status_codes:
                    status_codes[transaction.http_rc] = 0.0
                if not transaction.http_rc in all_status_codes:
                    all_status_codes[transaction.http_rc] = 0.0
                status_codes[transaction.http_rc] += 1.0
                all_status_codes[transaction.http_rc] += 1.0

            # calculate per-transaction metrics
            graphite_path = "%s.%s.%s" % (
                self._get_graphite_prefix(), tx_name, PFX_PERSEC_BYTES)
            metrics[graphite_path] = bytes_downloaded / self.config.carbon_interval_seconds
            graphite_path = "%s.%s.%s" % (
                self._get_graphite_prefix(), tx_name, PFX_PERSEC_CONNECTIONS)
            metrics[graphite_path] = new_connections / self.config.carbon_interval_seconds
            for response_code in status_codes:
                graphite_path = "%s.%s.%s%s" % (self._get_graphite_prefix(),
                                                tx_name,
                                                PFX_PERSEC_HTTP_RC,
                                                response_code)
                metrics[graphite_path] = status_codes[response_code] / self.config.carbon_interval_seconds

        # calculate 'all transactions' metrics
        graphite_path = "%s.%s.%s" % (
            self._get_graphite_prefix(), ALL_TRANSACTIONS, PFX_PERSEC_BYTES)
        metrics[graphite_path] = all_bytes_downloaded / self.config.carbon_interval_seconds
        graphite_path = "%s.%s.%s" % (
            self._get_graphite_prefix(), ALL_TRANSACTIONS, PFX_PERSEC_CONNECTIONS)
        metrics[graphite_path] = all_new_connections / self.config.carbon_interval_seconds
        for rc in all_status_codes:
            graphite_path = "%s.%s.%s%s" % (self._get_graphite_prefix(),
                                            ALL_TRANSACTIONS,
                                            PFX_PERSEC_HTTP_RC,
                                            rc)
            metrics[graphite_path] = all_status_codes[rc] / self.config.carbon_interval_seconds

    def _process_latency_metrics(self, metrics):
        """
        <tx name>
        **  latency
        **      mean_time
        **      percentile
        **          <specific percentiles defined in config>
        **      group
        **          <response time groups defined in config>
                http
                    resolve_host
                        mean_time
                    establish_connection
                        mean_time
                    first_byte
                        mean_time

        Reslolve host and establish connection times only count in cases
        where there is a new connection.
        """
        NonHTTPAggregator._process_latency_metrics(self, metrics)
        all_resolve_host_time = 0.0
        all_establish_conn_time = 0.0
        all_first_byte_time = 0.0
        all_new_connections = 0.0
        all_tests = 0.0
        for tx_name in self.transaction_data:
            resolve_host_time = 0.0
            establish_conn_time = 0.0
            first_byte_time = 0.0
            new_connections = 0.0
            for transaction in self.transaction_data[tx_name]:
                all_tests += 1.0
                first_byte_time += transaction.first_byte_time
                all_first_byte_time += transaction.first_byte_time
                if transaction.new_connections:
                    new_connections += 1.0
                    all_new_connections += 1.0
                    resolve_host_time += transaction.resolve_host_time
                    all_resolve_host_time += transaction.resolve_host_time
                    establish_conn_time += transaction.establish_connect_time
                    all_establish_conn_time += transaction.establish_connect_time
            graphite_path = "%s.%s.%s" % (
                self._get_graphite_prefix(), tx_name, PFX_LATENCY_HTTP_FIRST_BYTE)
            metrics[graphite_path] = first_byte_time / float(len(self.transaction_data[tx_name]))
            if new_connections:
                graphite_path = "%s.%s.%s" % (
                    self._get_graphite_prefix(), tx_name, PFX_LATENCY_HTTP_RESOLVE_HOST)
                metrics[graphite_path] = resolve_host_time / new_connections
                graphite_path = "%s.%s.%s" % (
                    self._get_graphite_prefix(), tx_name, PFX_LATENCY_HTTP_EST_CONN)
                metrics[graphite_path] = establish_conn_time / new_connections
        graphite_path = "%s.%s.%s" % (
            self._get_graphite_prefix(), ALL_TRANSACTIONS, PFX_LATENCY_HTTP_FIRST_BYTE)
        metrics[graphite_path] = all_first_byte_time / all_tests
        if all_new_connections:
            graphite_path = "%s.%s.%s" % (
                self._get_graphite_prefix(), ALL_TRANSACTIONS, PFX_LATENCY_HTTP_RESOLVE_HOST)
            metrics[graphite_path] = all_resolve_host_time / all_new_connections
            graphite_path = "%s.%s.%s" % (
                self._get_graphite_prefix(), ALL_TRANSACTIONS, PFX_LATENCY_HTTP_EST_CONN)
            metrics[graphite_path] = all_establish_conn_time / all_new_connections
