import os
import boto
import boto.sdb
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message
from boto.s3.connection import S3Connection, Location
from boto.s3.key import Key
import gflags
import json
import urllib2
from tempfile import mktemp
import commands

FLAGS = gflags.FLAGS


gflags.DEFINE_string('source', None, 'Select SQS queue source')
gflags.DEFINE_multistring('targets', [], 'Select SQS queue target')
gflags.DEFINE_boolean('delete', False, 'Remove items from queue when done processing?')
gflags.DEFINE_string('region', 'us-west-1', 'AWS region to connect to')
gflags.DEFINE_string('bucket_region', Location.USWest, 'AWS region to create S3 bucket')
gflags.DEFINE_string('bucket_in', None, 'Bucket name')
gflags.DEFINE_string('bucket_out', None, 'Bucket name')

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


    sqs = boto.sqs.connect_to_region(FLAGS.region)
    q = sqs.create_queue(FLAGS.source)
    targets = map(sqs.create_queue, FLAGS.targets)
    bucket = s3.get_bucket(FLAGS.bucket_in)
    bucket_out = s3.get_bucket(FLAGS.bucket_out)

    incomings = q.get_messages()
    while incomings:
        for incoming in incomings:
            fn = None
            message = json.loads(incoming.get_body())                       
            try:
                fn = mktemp()
                print "fetching", message['id']
                bucket.get_key(message['id']).get_contents_to_filename(fn)
                k = Key(bucket_out)
                k.key = message['id']
                data = commands.getoutput('exiv2 -pt ' + fn)
                k.set_contents_from_string(data)
            finally:
                if fn:
                    if os.path.exists(fn):
                        os.unlink(fn)


            for target in targets:
                target.write(incoming)
            q.delete_message(incoming)
        incomings = q.get_messages()
        
            

