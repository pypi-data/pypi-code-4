import boto
import boto.sdb
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

import gflags
import time 
import datetime
import json

FLAGS = gflags.FLAGS


gflags.DEFINE_string('source', "foliage", 'Select SQS queue source')
gflags.DEFINE_multistring('targets', ["download_originals", "download_thumbnails"], 'Select SQS queue target')
gflags.DEFINE_string('region', 'us-west-1', 'AWS region to connect to')
gflags.DEFINE_string('domain', 'foliage', 'Domain')


def main(argv=None, stdin=None, stdout=None, stderr=None):
    import sys
    argv = argv or sys.argv
    stdin = stdin or sys.stdin
    stdout = stdout or sys.stdout
    stderr = stderr or sys.stderr

    try:
        argv = FLAGS(argv)[1:]
    except gflags.FlagsError, e:
        stderr.write("%s\\nUsage: %s update_id_addresses\\n%s\n" %
                     (e, sys.argv[0], FLAGS))
        return 1
    sqs = boto.sqs.connect_to_region(FLAGS.region)
    q = sqs.create_queue(FLAGS.source)
    targets = map(sqs.create_queue, FLAGS.targets)
    simpledb = boto.sdb.connect_to_region(FLAGS.region)
    domain = simpledb.create_domain(FLAGS.domain)
    
    incomings = q.get_messages()
    while incomings:
        for incoming in incomings:
            message = json.loads(incoming.get_body())
            print message
            domain.put_attributes(message['id'], message)
            for target in targets:
                target.write(incoming)
            q.delete_message(incoming)
        incomings = q.get_messages()
        
            

