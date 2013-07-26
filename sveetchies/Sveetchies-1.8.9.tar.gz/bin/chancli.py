#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Command Line Interface for PyChanDownloader
"""
from Sveetchies.chan.cli import DownloadCLI

#
#
if __name__ == "__main__":
    obj = DownloadCLI()
    obj.get_commandline_options()
    obj.launch()
