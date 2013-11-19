#!/usr/bin/env python

"""
Unit tests for the veracity package.
"""

import os
import sys
import time
import shutil
import logging
import tempfile
import subprocess
from pprint import pformat

from veracity import vv
from veracity import objects
from veracity import settings

TEST = os.path.dirname(os.path.abspath(__file__))
FILES = os.path.join(TEST, 'files')

TEST_REPO_NAME = 'python-veracity-test'  # repository for integration tests
REASON = "no test repository available"


def log(*objs):
    """Logs object representations during testing.
    """
    for obj in objs:
        logging.info("log: {0}".format(pformat(obj)))


def create_temp_repo(module):
    """Clone the test repository for a module's integration tests.
    """
    if TEST_REPO:
        sys.stderr.write('\n' +
                         "Cloning test repository for {0}...".format(module) +
                         '\n\n')
        name = "{0}-{1}-{2}".format(TEST_REPO.name, module, int(time.time()))
        temp = TEST_REPO.clone(name, autosync=False)
        temp.user = 'testuser'
        return temp


def delete_temp_repo(module, repo):
    """Delete the test repository clone.
    """
    if repo:
        sys.stderr.write('\n' +
                         "Deleting test repository for {0}...".format(module) +
                         '\n\n')
        repo.delete()


def _create_repo():
    """Creates a test repository for integration tests.
    """
    if TEST_REPO_NAME in vv.repos():
        return

    sys.stderr.write('\n' +
                     "Creating a test repository for integration tests..." +
                     '\n\n')

    # Initialize a new repository
    subprocess.call(['vv', 'repo', 'new', TEST_REPO_NAME])
    subprocess.call(['vv', 'config', 'set',
                     '/instance/{0}/paths/default'.format(TEST_REPO_NAME),
                     TEST_REPO_NAME])

    # Check out to a temporary location
    temp = tempfile.mkdtemp()
    os.chdir(temp)
    subprocess.call(['vv', 'checkout', TEST_REPO_NAME])

    # Commit 1
    with open("foo.h", 'w') as new:
        new.write("this is foo.h")
    with open("bar.c", 'w') as new:
        new.write("this is ")
    subprocess.call(['vv', 'addremove'])
    subprocess.call(['vv', 'whoami', '--create', 'testuser'])
    subprocess.call(['vv', 'commit', '--message', "added sample files"])

    # Commit 2
    with open("bar.c", 'a') as new:
        new.write("bar.c ")
    subprocess.call(['vv', 'commit', '--message', "added missing text"])

    # Initialize build configuration
    os.chdir(os.path.dirname(os.path.dirname(__file__)))
    subprocess.call([sys.executable, 'vscript.py', TEST_REPO_NAME])

    # Cleanup
    shutil.rmtree(temp)
    sys.stderr.write('\n')


def _delete_repo():
    """Delete the test repository.
    """
    if TEST_REPO_NAME not in vv.repos():
        return

    sys.stderr.write('\n' +
                     "Deleting the test repository for integration tests..." +
                     '\n\n')

    # Delete the repository
    subprocess.call(['vv', 'repo', 'delete', TEST_REPO_NAME])


# Create a test repository to run integration/unit, delete for only unit
if settings.CREATE_TEST_REPO:
    _create_repo()
elif settings.DELETE_TEST_REPO:
    _delete_repo()

# Set the integration test repository if enabled and created
if settings.TEST_INTEGRATION and TEST_REPO_NAME in vv.repos():
    TEST_REPO = objects.Repository(TEST_REPO_NAME)
    TEST_REPO.user = 'testuser'
else:
    TEST_REPO = None
