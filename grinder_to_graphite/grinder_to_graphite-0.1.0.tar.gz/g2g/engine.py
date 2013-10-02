
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

from g2g import g2g_config
from g2g.logtype.grinder import transaction
from g2g.logtype.grinder import mapping_reader
from g2g.logtype.grinder import column_map
from g2g.aggregator.http import HTTPAggregator
from g2g.aggregator.non_http import NonHTTPAggregator
from pygtail import Pygtail
import time
import os
import sys
import logging as log

_ingest_invocations = 0


class Engine(object):

    def __init__(self, config):
        self.config = config
        map_reader = mapping_reader.MapReader()
        self.tx_name_map = map_reader.get_tx_names(config.mapping_file)
        if self._is_grinder_log_http(config.data_file):
            self.grinder_transaction_class = transaction.HTTPTest   # class, not an instance
            self.aggregator_class = HTTPAggregator
        else:
            self.grinder_transaction_class = transaction.NonHTTPTest
            self.aggregator_class = NonHTTPAggregator

    def _is_grinder_log_http(self, data_file):
        if not os.path.exists(data_file):
            log.critical("FATAL: data file '%s' not found." % data_file)
            sys.exit(1)
        if not os.access(data_file, os.R_OK):
            log.critical("FATAL: cannot read config file '%s'" % data_file)
            sys.exit(1)
        stream = open(data_file)
        first_line = stream.readline()
        stream.close()
        words = first_line.split(",")
        if len(words) > 10:
            log.info("HTTP grinder log detected.")
            return True
        log.info("Non-HTTP grinder log detected.")
        return False

    def _get_offset_file(self, data_file):
        if not os.path.exists(data_file):
            log.warn("Data file %s not found" % data_file)
            return None
        if data_file.startswith(os.sep):
            data_file = data_file[1:]
        offset_file = ".".join(data_file.split(os.sep))
        offset_file = g2g_config.DOTDIR + os.sep + offset_file + ".offset"
        return offset_file

    def _get_first_data_line(self, data_file):
        if not os.path.exists(data_file):
            log.critical("FATAL: data file '%s' not found." % data_file)
            sys.exit(1)
        # skip to the first valid line
        stream = open(data_file)
        if not stream.readline():
            log.critical("Could not read data file '%s'" % data_file)
            sys.exit(1)
        line = stream.readline()
        if not line:
            log.critical("Invalid data file")
            sys.exit(1)
        stream.close()
        return line

    def _get_timestamp(self, words):
        # example:
        # 2, 0, 1, 1321056277917, 217, 0, 302, 0, 0, 29, 97, 124
        if len(words) > 3:
            return int(words[3][:13]) / 1000
        return None

    def _ingest_log(self, graphite_aggregator, test_mode=False):
        """
        Read the unchanged lines in the log file a single time

        Returns the timestamp from the last line read.
        """
        if test_mode:
            global _ingest_invocations
            _ingest_invocations += 1
        timestamp = None
        data_file = self.config.data_file
        offset_file = self._get_offset_file(data_file)
        log.debug("file: %s, offset: %s" % (data_file, offset_file))
        for line in Pygtail(data_file, offset_file=offset_file):
            if line.startswith("Thread"):  # we're at the start of the file
                continue
            words = line.split(", ")
            timestamp = self._get_timestamp(words)
            if timestamp > graphite_aggregator.report_time:
                graphite_aggregator.report_to_graphite()
            tx = self.grinder_transaction_class(words)
            tx_name = self.tx_name_map[words[column_map.TEST_NUMBER]]
            graphite_aggregator.add_transaction(tx_name, tx)
        return timestamp

    def ingest_log(self, test_mode=False):
        """
        Reads through the data file from start to finish.  Analyzes
        each line using the specified line analyzer.  Checks the
        data file for new data, and reads the changed part as needed.

        Returns: timestamps for the first and last log file entries

        """
        data_file = self.config.data_file
        if self.config.resume:
            log.warn("Reading data file %s from the last read location." % data_file)
        else:
            offset_file = self._get_offset_file(data_file)
            if os.path.exists(offset_file):
                os.remove(offset_file)
            log.warn("Reading data file %s from the beginning." % data_file)
        if self.config.follow:
            log.warn("Will monitor %s for new entries forever." % data_file)

        line = self._get_first_data_line(data_file)
        start_timestamp = self._get_timestamp(line.split())
        graphite_aggregator = self.aggregator_class(start_timestamp, self.config)
        end_timestamp = self._ingest_log(graphite_aggregator, test_mode)
        while self.config.follow:
            log.warn("Waiting %d seconds" % self.config.follow_interval_seconds)
            time.sleep(self.config.follow_interval_seconds)
            _end_timestamp = self._ingest_log(graphite_aggregator, test_mode)
            if _end_timestamp:
                end_timestamp = _end_timestamp
            if test_mode:  # don't follow forever if we're in test mode
                break
        return (start_timestamp, end_timestamp)
