
# Copyright (C) 2011-2013, Travis Bear
# All rights reserved.
#
# This file is part of Graphite Log Feeder.
#
# Graphite Log Feeder is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# Graphite Log Feeder is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with Graphite Log Feeder; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA


from glf.feeder import aggregator
from glf import config_param as param
import glf_config
from pygtail import Pygtail
import time
import os


def _get_offset_file(data_file):
    if not os.path.exists(data_file):
        print "Data file %s not found" %data_file
        return None
    if data_file.startswith(os.sep):
        data_file = data_file[1:]
    offset_file = ".".join(data_file.split(os.sep))
    offset_file = glf_config.DOTDIR + os.sep + offset_file +  ".offset"
    return offset_file

def _ingest_log(line_reader, data_file, graphite_aggregator):
    """
    Read the unchanged lines in the log file a single time
    """
    words = []      # scope is required outside the loop
    for line in Pygtail(data_file, offset_file=_get_offset_file(data_file)):
        if line.startswith("Thread"): # we're at the start of the file
            continue
        words = line.split()
        timestamp = line_reader.get_timestamp(words)
        for tx_tuple in line_reader.get_counter_metrics(words):
            graphite_aggregator.update_counter_metric(tx_tuple[0], tx_tuple[1])
        timer_metrics = line_reader.get_timer_metrics(words)
        # a line may or may not contain timed metrics
        if timer_metrics:
            for tx_tuple in timer_metrics:
                # [0] = tx name, [1] = timing data
                graphite_aggregator.update_timer_metric(tx_tuple[0], tx_tuple[1])
        if timestamp > graphite_aggregator.report_time:
            graphite_aggregator.report_to_graphite()
    return line_reader.get_timestamp(words)



def ingest_log(line_reader, config):
    """
    Reads through the data file from start to finish.  Analyzes
    each line using the specified line analyzer.  Checks the
    data file for new data, and reads the changed part as needed.
        
    Returns: timestamps for the first and last log file entries
    """
    data_file = config.get(param.DATA_SECTION, param.LOG_FILE)
    if config.get(param.DATA_SECTION, param.RESUME).lower().startswith("f"):
        offset_file = _get_offset_file(data_file)
        if os.path.exists(offset_file):
            os.remove(offset_file)
        print "Reading data file %s from the beginning." %data_file
    else:
        print "Reading data file %s from the last read location." %data_file
    if config.get(param.DATA_SECTION, param.FOLLOW_DATA_FILE).lower().startswith("t"):
        print "Will monitor %s for new entries forever." %data_file
    
    stream = open(data_file)
    line = line_reader.get_first_data_line(stream)
    #print "--->%s<---" %line
    start_timestamp = line_reader.get_timestamp(line.split())
    graphite_aggregator = aggregator.GraphiteAggregator(start_timestamp, config)
    stream.close()
    sleep_time = float(config.get(param.DATA_SECTION, param.FOLLOW_INTERVAL_SECONDS))
    end_timestamp = _ingest_log(line_reader, data_file, graphite_aggregator)
    while config.get(param.DATA_SECTION, param.FOLLOW_DATA_FILE).lower().startswith("t"):
        print "Waiting %d seconds" %sleep_time
        time.sleep(sleep_time)
        _end_timestamp = _ingest_log(line_reader, data_file, graphite_aggregator)
        if _end_timestamp:
            end_timestamp = _end_timestamp
    return (start_timestamp, end_timestamp)
