# Copyright (c) 2012 Ian C. Good
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
# THE SOFTWARE.
#

"""Package implementing the :mod:`~slimta.queue` storage system using redis_.

.. _redis: http://redis.io/

"""

from __future__ import absolute_import

import os
import uuid
import cPickle

import redis
import gevent
from gevent import socket

from slimta.queue import QueueStorage 
from slimta import logging

__all__ = ['RedisStorage']

log = logging.getQueueStorageLogger(__name__)


class GeventConnection(redis.Connection):

    def _connect(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(self.socket_timeout)
        sock.connect((self.host, self.port))
        return sock


class RedisStorage(QueueStorage):
    """|QueueStorage| mechanism that stores |Envelope| and queue metadata in
    redis hashes.

    :param host: Hostname of the redis server to connect to.
    :param port: Port to connect to.
    :param db: Database number to create keys in.
    :param password: Optional password to authenticate with.
    :param socket_timeout: Timeout, in seconds, for socket operations. If the
                           timeout is hit, :py:exc:`socket.timeout` is raised.
                           ``None`` disables the timeout.
    :param prefix: Any key created is prefixed with this string.
    :type prefix: str

    """

    HOLD_STRING = 'held'

    def __init__(self, host='localhost', port=6379, db=0, password=None,
                 socket_timeout=None, prefix='slimta:'):
        super(RedisStorage, self).__init__()
        pool = redis.ConnectionPool(connection_class=GeventConnection,
                                    host=host, port=port, db=db,
                                    password=password,
                                    socket_timeout=socket_timeout)
        self.redis = redis.StrictRedis(connection_pool=pool)
        self.prefix = prefix
        self.queue_key = '{0}queue'.format(prefix)

    def write(self, envelope, timestamp):
        envelope_raw = cPickle.dumps(envelope, cPickle.HIGHEST_PROTOCOL)
        while True:
            id = uuid.uuid4().hex
            key = self.prefix + id
            if self.redis.setnx(key, self.HOLD_STRING):
                queue_raw = cPickle.dumps((timestamp, id),
                                          cPickle.HIGHEST_PROTOCOL)
                pipe = self.redis.pipeline()
                pipe.delete(key)
                pipe.hmset(key, {'timestamp': timestamp,
                                 'attempts': 0,
                                 'envelope': envelope_raw})
                pipe.rpush(self.queue_key, queue_raw)
                pipe.execute()
                log.write(id, envelope)
                return id

    def set_timestamp(self, id, timestamp):
        self.redis.hset(self.prefix+id, 'timestamp', timestamp)
        log.update_meta(id, timestamp=timestamp)

    def increment_attempts(self, id):
        new_attempts = self.redis.hincrby(self.prefix+id, 'attempts', 1)
        log.update_meta(id, attempts=new_attempts)
        return new_attempts

    def load(self):
        for key in self.redis.keys(self.prefix+'*'):
            if key != self.queue_key:
                id = key[len(self.prefix):]
                timestamp = float(self.redis.hget(key, 'timestamp'))
                yield timestamp, id

    def get(self, id):
        envelope_raw, attempts = self.redis.hmget(self.prefix+id,
                                                  'envelope', 'attempts')
        return cPickle.loads(envelope_raw), int(attempts)

    def remove(self, id):
        self.redis.delete(self.prefix+id)
        log.remove(id)

    def notify(self, id, timestamp):
        pass

    def wait(self):
        ret = self.redis.blpop([self.queue_key], 0)
        if ret:
            return cPickle.loads(ret[1])


# vim:et:fdm=marker:sts=4:sw=4:ts=4
