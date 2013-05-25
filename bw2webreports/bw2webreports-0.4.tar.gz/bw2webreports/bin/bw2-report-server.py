#!/usr/bin/env python
# encoding: utf-8
"""Brightway2 web user interface.

Usage:
  bw2-report-server.py <data_dir> [--port=<port>] [--local]
  bw2-report-server.py -h | --help
  bw2-report-server.py --version

Options:
  -h --help     Show this screen.
  --version     Show version.
  --local       Only listen to connections from localhost

"""
from bw2webreports import report_server
from docopt import docopt
from werkzeug.serving import run_simple
import os

if __name__ == "__main__":
    print "Starting report server"
    args = docopt(__doc__, version='Brightway2 Reports Server 0.1')
    port = int(args.get("--port", False) or 8000)
    data_dir = os.path.abspath(args["<data_dir>"])
    if not os.path.exists(data_dir):
        raise OSError("Can't find or understand `data_dir`")
    report_server.config['DATA_DIR'] = data_dir
    logs_dir = os.path.join(data_dir, "logs")
    report_server.config['LOGS_DIR'] = logs_dir
    if not os.path.exists(logs_dir):
        os.mkdir(logs_dir)
    url = "localhost" if args["--local"] else "0.0.0.0"
    run_simple(url, port, report_server)
