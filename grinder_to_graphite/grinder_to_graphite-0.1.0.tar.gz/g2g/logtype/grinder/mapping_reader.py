
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


"""
This module extracts useful information from the grinder
mapping log file.  With current versions of the grinder,
these logs' default name is <hostname>-0.log
"""

from mtfileutil.reverse import reverseSeek
import os
import sys
import logging as log

ALL_TRANSACTIONS = "All_Transactions"
TABLE_MARKER = "Final statistics for this process"


class MapReader:
    """
    Examines the table at the end of the Grinder mapping file
    returns a dict
        key: tx number
        value: tx name
    """
    def get_tx_names(self, map_file):
        log.warn("  ====   getting map from %s" % map_file)
        if not os.path.exists(map_file):
            log.critical("Grinder mapping file '%s' can't be found." % map_file)
            sys.exit(1)
        tx_num_name_map = {}  # key: tx number, val: tx name
        line_name_map = {}    # key: data line, val: tx name
        final_out_lines = reverseSeek(map_file, TABLE_MARKER)
        for line in final_out_lines:
            if line.find("Test") == 0 or line.find("Test") == 1 or line.startswith("Totals"):
                if line.startswith("Totals"):
                    # Format the totals line to be identical to test lines
                    line = line.replace("Totals", "Totals 0")  # add a column
                    line = '%s "%s"' % (line, ALL_TRANSACTIONS)
                testName = self._get_initial_tx_name(line)
                line_name_map[line] = testName
        if len(line_name_map) == 0:
            msg = """
                Incomplete or corrupted grinder out file.  No summary data containing
                test number/name mappings found."""
            log.critical(msg)
            sys.exit(1)

        duplicate_tx_names = self._get_duplicates(line_name_map.values())
        if len(duplicate_tx_names) > 0:
            log.info("Duplicate transaction names found: %s" % duplicate_tx_names)
        for line in line_name_map.keys():
            tx_name = self._get_initial_tx_name(line).replace(' ', '_')
            txNum = self._get_tx_num(line)
            if duplicate_tx_names.__contains__(tx_name):
                tx_name = "%s_%s" % (tx_name, txNum)
            tx_num_name_map[txNum] = tx_name
            line_name_map[line] = tx_name
        log.info("Final tx names: %s" % tx_num_name_map.values())
        return tx_num_name_map

    def _get_initial_tx_name(self, line):
        return line.split('"')[1]   # test names appear in quotes

    def _get_tx_num(self, line):
        return line.split(" ")[1]  # test number is 2nd column

    def _get_duplicates(self, tx_names):
        """
        Returns a subset of tx_names containing items that appear more than once
        """
        itemCountMap = {}
        for item in tx_names:
            if item in itemCountMap:
                itemCountMap[item] += 1
            else:
                itemCountMap[item] = 1
        return [key for key in itemCountMap.keys() if itemCountMap[key] > 1]
