#!/usr/bin/env python

"""
Unit tests for the veracity package.
"""

import os
import logging
from pprint import pformat

from veracity import vv
from veracity import objects
from veracity import common
from veracity import settings

TEST = os.path.dirname(os.path.abspath(__file__))
FILES = os.path.join(TEST, 'files')

TEST_REPO_NAME = 'python-veracity-test'  # repository for integration tests
REASON = "no test repository available"
if settings.CREATE_TEST_REPO and TEST_REPO_NAME not in vv.repos():
    common.create_test_repo(TEST_REPO_NAME)
if TEST_REPO_NAME in vv.repos():
    TEST_REPO = objects.Repository('python-veracity-test')
else:
    TEST_REPO = None


def log(*objs):
    """Logs object representations during testing."""
    for obj in objs:
        logging.info("log: {0}".format(pformat(obj)))
