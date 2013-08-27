#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Exceptions related to `chzip`"""

class DownloadException(Exception):
    """Exception raised when a problem when downloading a file occured."""


class UpgradeException(Exception):
    """Exception raised to signal a failure in the upgrade process."""
