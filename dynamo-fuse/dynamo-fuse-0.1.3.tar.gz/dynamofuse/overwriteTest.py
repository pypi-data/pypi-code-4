from __future__ import with_statement

__author__ = 'Denis Mikhalkin'

from posix import R_OK, X_OK, W_OK
from errno import *
from os.path import realpath
from sys import argv, exit
from threading import Lock
import boto.dynamodb
from boto.dynamodb.exceptions import DynamoDBKeyNotFoundError, DynamoDBConditionalCheckFailedError
from boto.exception import BotoServerError, BotoClientError
from boto.exception import DynamoDBResponseError
from stat import *
from boto.dynamodb.types import Binary
from time import time, sleep
from boto.dynamodb.condition import EQ, GT
import os
from fuse import FUSE, FuseOSError, Operations, LoggingMixIn, fuse_get_context
from io import FileIO
import logging
from logging import StreamHandler, FileHandler
import sys
import cStringIO
import itertools
import traceback
from threading import Thread

if not hasattr(__builtins__, 'bytes'):
    bytes = str

def performTest():
    conn = boto.dynamodb.connect_to_region("ap-southeast-2", aws_access_key_id=os.environ['AWS_ACCESS_KEY_ID'],
        aws_secret_access_key=os.environ['AWS_SECRET_ACCESS_KEY'])
    table = conn.get_table("DynamoFS")

    item1 = table.new_item("/", "b", attrs={"flag":"item1", "version":1})
    item1.put()
    item1 = table.get_item("/", "b")
    table.get_item("/", "b").delete()
    item1["flag"] = "updated"
#    item1.save(expected_value={"path":item1["path"], "name":item1["name"]})
    try:
        item1.save(expected_value={"version":item1["version"]})
    except DynamoDBConditionalCheckFailedError:
        item1 = table.get_item("/", "b")

if __name__ == '__main__':
    performTest()