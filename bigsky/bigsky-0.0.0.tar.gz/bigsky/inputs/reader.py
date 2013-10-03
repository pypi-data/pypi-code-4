import boto
from boto.sqs.connection import SQSConnection
from boto.sqs.message import Message

import flickr
import gflags
import time 
import datetime
import json

FLAGS = gflags.FLAGS

gflags.DEFINE_float('east', None, 'Longitude of eastern most edge of bounding box')
gflags.DEFINE_float('west', None, 'Longitude of western most edge of bounding box')
gflags.DEFINE_float('north', None, 'Latitude of northern most edge of bounding box')
gflags.DEFINE_float('south', None, 'Latitude of southern most edge of bounding box')
gflags.DEFINE_enum('source', 'flickr', ['flickr'], 'Select image source.')
gflags.DEFINE_string('target', None, 'Select SQS queue target')
gflags.DEFINE_integer('limit', 1000000, 'Maximum number of photos to fetch')
gflags.DEFINE_integer('year', None, 'Year')
gflags.DEFINE_integer('month', None, 'Month')
gflags.DEFINE_integer('day', None, 'Day')
gflags.DEFINE_string('region', 'us-west-1', 'AWS region to connect to')
gflags.DEFINE_float('delay', 1, 'Seconds to wait between API calls.  Note there is a 3,600 query per hour limit, so going faster will just earn you a status 420 enhance your calm message.')


GET_PHOTOS_DISPATCHER = dict(flickr=flickr.get_photos)
def get_photos():
    
    all_flags = (FLAGS.south, FLAGS.west, FLAGS.north, FLAGS.east)
    kwargs = dict(
                  per_page=500,   # Limit for geocoded stuff
                  )
                  
                  
    if all(all_flags):
        kwargs['bbox'] = '%0.4f, %0.4f, %0.4f, %0.4f' % all_flags
        
    kwargs['min_taken_date'] = int(datetime.datetime(year=FLAGS.year, month=FLAGS.month, day=FLAGS.day, hour=11, minute=0, second=0).strftime('%s'))
    kwargs['max_taken_date'] = int(datetime.datetime(year=FLAGS.year, month=FLAGS.month, day=FLAGS.day, hour=14, minute=0, second=0).strftime('%s'))
    x = 0
    while True:
        print kwargs
        kwargs['page'] = str(x)
        x += 1 
        photos = list(GET_PHOTOS_DISPATCHER[FLAGS.source](**kwargs))
        if not photos:
            break
        for photo in photos:
            yield photo


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

    conn = boto.sqs.connect_to_region(FLAGS.region)
    q = conn.create_queue(FLAGS.target)
    output = []
    for photo in get_photos():
        print photo
        m = Message()
        m.set_body(json.dumps(photo))
        q.write(m)


    return 0
