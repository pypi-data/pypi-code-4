#!/usr/bin/env python

"""
Settings for the veracity package.
"""

import os
import logging

# Logging settings
DEFAULT_LOGGING_FORMAT = "%(message)s"
VERBOSE_LOGGING_FORMAT = "%(levelname)s: %(message)s"
VERBOSE2_LOGGING_FORMAT = "%(asctime)s: %(levelname)s: %(message)s"
VERBOSE3_LOGGING_FORMAT = "%(asctime)s: %(levelname)s: %(module)s:%(lineno)d: %(message)s"  # pylint: disable=C0301
DEFAULT_LOGGING_LEVEL = logging.INFO
VERBOSE_LOGGING_LEVEL = logging.DEBUG

# Path settings
VV_PATH_WINDOWS = r"C:\Program Files\SourceGear\Veracity\vv.exe"
VSCRIPT_PATH_WINDOWS = r"C:\Program Files\SourceGear\Veracity\vscript.exe"

# Synchronization settings
AUTO_PULL = True  # pull before operations that access the repository
AUTO_PUSH = True  # push after operations that modify the repository
MIN_DELAY = 30  # delay automatic pulls/pushes by at least this many seconds

# Builder settings
POLL_DELAY = 5  # number of seconds to delay between looking for changesets
BUILD_DELAY = 5  # number of seconds to delay between looking for builds
MAX_BUILDS = 50  # maximum number of builds to check when listing all builds

# Test repository settings
TEST_INTEGRATION = os.getenv('TEST_INTEGRATION')  # enable integration tests
CREATE_TEST_REPO = True  # create the test repository for integration tests
DELETE_TEST_REPO = False  # delete the test repository and only run unit tests
