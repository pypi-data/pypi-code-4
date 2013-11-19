# -*- coding: utf-8 -*-
from nose.tools import *
try:
    from Queue import Queue
except ImportError:
    from queue import Queue
from datetime import datetime
from relshell.timestamp import Timestamp
from relshell.timespan import Timespan
from relshell.record import Record
from relshell.recorddef import RecordDef
from relshell.error import TimestampError
from relshell.batch import Batch


def test_batch_timestamp_check_ok():
    t     = Timestamp(datetime.now())
    tspan = Timespan(t, 10)
    rdef  = RecordDef([{'name': 'col0', 'type': 'INT'}])

    q = Queue()
    q.put(Record(rdef, 123, timestamp=t))
    q.put(Record(rdef, 123, timestamp=t + 5))
    q.put(Record(rdef, 123, timestamp=t + 10))
    q.put(None)  # `record_q` argument of `Batch` must have None as last element

    batch = Batch(tspan, q, timestamp_check=True)


@raises(TimestampError)
def test_batch_timestamp_check_ng():
    t     = Timestamp(datetime.now())
    tspan = Timespan(t, 10)
    rdef  = RecordDef([{'name': 'col0', 'type': 'INT'}])

    q = Queue()
    q.put(Record(rdef, 123, timestamp=t))
    q.put(Record(rdef, 123, timestamp=t - 3))  # NG!
    q.put(Record(rdef, 123, timestamp=t + 10))
    q.put(None)  # `record_q` argument of `Batch` must have None as last element

    batch = Batch(tspan, q, timestamp_check=True)
