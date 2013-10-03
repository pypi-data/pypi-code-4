import boto
import boto.sdb
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from boto.s3.connection import S3Connection, Location
import boto.s3
from boto.s3.key import Key
import gflags
import json
import urllib2
import os
from tempfile import mktemp
FLAGS = gflags.FLAGS


gflags.DEFINE_string('source', None, 'Select SQS queue source')
gflags.DEFINE_multistring('targets', [], 'Select SQS queue target')
gflags.DEFINE_boolean('delete', False, 'Remove items from queue when done processing?')
gflags.DEFINE_string('region', 'us-west-1', 'AWS region to connect to')
gflags.DEFINE_string('bucket_region', Location.USWest, 'AWS region to create S3 bucket')
gflags.DEFINE_string('bucket', None, 'Bucket name')
gflags.DEFINE_string('url', None, 'Field to find url')

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
    s3 = boto.s3.connect_to_region(FLAGS.bucket_region)

    try:
        bucket = s3.create_bucket(FLAGS.bucket, location=FLAGS.bucket_region)
    except boto.exception.S3CreateError:
        bucket = s3.get_bucket(FLAGS.bucket)

    sqs = boto.sqs.connect_to_region(FLAGS.region)
    q = sqs.create_queue(FLAGS.source)
    targets = map(sqs.create_queue, FLAGS.targets)
    
    incomings = q.get_messages()
    while incomings:
        for incoming in incomings:
            message = json.loads(incoming.get_body())
            if FLAGS.url not in message:
                print "Skipping ", message
                q.delete_message(incoming)
                continue
                
            print "Downloading", message[FLAGS.url]
            data = urllib2.urlopen(message[FLAGS.url]).read()
            k = Key(bucket)
            k.key = str(message['id'])
            print "Saving", message['id'], len(data), message[FLAGS.url]
            k.set_contents_from_string(data)
            for target in targets:
                target.write(incoming)
            q.delete_message(incoming)
        incomings = q.get_messages()
        
            

