
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

import os
import yaml
from os.path import expanduser
import logging.config
import logging as log

DOTDIR = "%s/.grinder2graphite" % expanduser("~")
DEFAULT_CONFIG_POINTER = "config_file"
if not os.path.isdir(DOTDIR):
    os.mkdir(DOTDIR)


class G2GConfiguration:
    """
    Utility class to flatten access to yaml configs and enable
    IDE autocompletes
    """
    def __init__(self, config_file, data=None):
        if not data:
            data = yaml.load(open(config_file), Loader=yaml.Loader)

        # logging
        logging.config.dictConfig(data["logging"])
        log.info("Initializing config")

        self.carbon_host = data["g2g"]["carbon"]["host"]
        self.carbon_port = data["g2g"]["carbon"]["port"]
        self.carbon_prefix = data["g2g"]["carbon"]["prefix"]
        self.carbon_suffix = data["g2g"]["carbon"]["suffix"]
        self.carbon_interval_seconds = data["g2g"]["carbon"]["interval_seconds"]
        self.data_file = data["g2g"]["data"]["log_file"]
        self.mapping_file = data["g2g"]["data"]["mapping_file"]

        # optional settings
        self.time_group_ms = []
        if "analysis" in data["g2g"] and "time_group_milliseconds" in data["g2g"]["analysis"]:
            self.time_group_ms = data["g2g"]["analysis"]["time_group_milliseconds"]
        self.response_time_percentiles = []
        if "analysis" in data["g2g"] and "response_time_percentiles" in data["g2g"]["analysis"]:
            self.response_time_percentiles = data["g2g"]["analysis"]["response_time_percentiles"]
        self.follow = False
        if "run" in data["g2g"] and "follow" in data["g2g"]["run"]:
            self.follow = data["g2g"]["run"]["follow"]
        self.follow_interval_seconds = 60
        if "run" in data["g2g"] and "follow_interval_seconds" in data["g2g"]["run"]:
            self.follow_interval_seconds = data["g2g"]["run"]["follow_interval_seconds"]
        self.resume = False
        if "run" in data["g2g"] and "resume" in data["g2g"]["run"]:
            self.resume = data["g2g"]["run"]["resume"]
        self.log_dict = None


def create_example_config_file(config_file="g2g.sample.yaml"):
    # Created in the current dir.  We can just barf on permission errors.
    stream = open(config_file, "w")
    text = """
# Grinder to Graphite configuration options.  See
# https://bitbucket.org/travis_bear/grinder_to_graphite for
# more info on what these do.
g2g:
    carbon:
        host: localhost
        port: 2003
        prefix: deleteme
        suffix: grinder
        interval_seconds: 10.0
    data:
        log_file: logs/hostname-0-data.log
        mapping_file: logs/hostname-0.log
    analysis:
        time_group_milliseconds: [100,200]
        response_time_percentiles: [0.5, 0.95, 0.99]
    run:
        follow: False
        follow_interval_seconds: 60
        resume: False



# Standard python logging configuration. For additional info, see
# http://docs.python.org/2/library/logging.config.html
logging:
    version: 1
    formatters:
        plainFormater:
            format: '%(message)s'
        basicFormater:
            format: '%(asctime)s - %(levelname)s: %(message)s'
            datefmt: '%Y/%m/%d %H:%M:%S'
    handlers:
        console:
            class: logging.StreamHandler
            formatter: plainFormater
            level: WARN
            stream: ext://sys.stdout
    loggers:
        clogger:
            level: DEBUG
            handlers: [console]
    root:
        level: DEBUG
        handlers: [console]
    """
    stream.write(text)
    stream.close()
    log.info("Generated sample config file at '%s'" % config_file)


def get_config(args, config_dir=DOTDIR, dotfilename=DEFAULT_CONFIG_POINTER):
    config_file = None
    if len(args) == 0:
        dotfile = "%s/%s" % (config_dir, dotfilename)
        if not os.path.exists(dotfile):
            log.warning("No default config specified.")
            log.info(dotfilename, dotfile)
            return None
        stream = open(dotfile)
        config_file = stream.read()
        stream.close()
        log.debug(config_file)
    else:
        config_file = args[0]
    if config_file is None:
        print ("WARNING: config file not found: %s" % config_file)
        return None
    if not os.path.exists(config_file):
        print ("WARNING: config file not found: %s" % config_file)
        return None
    if not os.access(config_file, os.R_OK):
        print ("WARNING: cannot read config file '%s'" % config_file)
        return None
    print("Loading config from %s" % config_file)
    return G2GConfiguration(config_file)


def set_default_config(config_file, config_dir=DOTDIR, dotfile=DEFAULT_CONFIG_POINTER):
    filename = "%s/%s" % (config_dir, dotfile)
    stream = open(filename, 'w')
    stream.write(config_file)
    stream.close()
