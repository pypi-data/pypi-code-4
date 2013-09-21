
import re
import cPickle

from redis import StrictRedis
from mox import MoxTestBase, IsA, Func

from slimta.redisstorage import RedisStorage
from slimta.envelope import Envelope

id_pattern = re.compile(r'^[0-9a-fA-F]{32}$')


def _is_id(string):
    return id_pattern.match(string)


def _is_prefixed_id(string):
    if string.startswith('test:'):
        return _is_id(string[5:])


class TestRedisStorage(MoxTestBase):

    def setUp(self):
        super(TestRedisStorage, self).setUp()
        self.storage = RedisStorage(prefix='test:')
        self.storage.redis = self.mox.CreateMock(StrictRedis)

    def _write_test_envelope(self, rcpts=None):
        return id, env

    def test_write(self):
        self.storage.redis.setnx(Func(_is_prefixed_id), IsA(str)).AndReturn(0)
        self.storage.redis.setnx(Func(_is_prefixed_id), IsA(str)).AndReturn(1)
        pipe = self.mox.CreateMockAnything()
        self.storage.redis.pipeline().AndReturn(pipe)
        pipe.delete(Func(_is_prefixed_id))
        def _verify_hmset(val):
            self.assertEqual(1234567890, val['timestamp'])
            self.assertEqual(0, val['attempts'])
            self.assertIsInstance(val['envelope'], basestring)
            return True
        pipe.hmset(Func(_is_prefixed_id), Func(_verify_hmset))
        def _verify_rpush(val):
            timestamp, id = cPickle.loads(val)
            self.assertEqual(1234567890, timestamp)
            self.assertTrue(_is_id(id))
            return True
        pipe.rpush('test:queue', Func(_verify_rpush))
        pipe.execute()
        self.mox.ReplayAll()
        env = Envelope('sender@example.com', ['rcpt@example.com'])
        env.timestamp = 9876543210
        self.storage.write(env, 1234567890)

    def test_set_timestamp(self):
        self.storage.redis.hset('test:asdf', 'timestamp', 1111)
        self.mox.ReplayAll()
        self.storage.set_timestamp('asdf', 1111)

    def test_increment_attempts(self):
        self.storage.redis.hincrby('test:asdf', 'attempts', 1).AndReturn(1)
        self.storage.redis.hincrby('test:asdf', 'attempts', 1).AndReturn(2)
        self.mox.ReplayAll()
        self.assertEqual(1, self.storage.increment_attempts('asdf'))
        self.assertEqual(2, self.storage.increment_attempts('asdf'))

    def test_get(self):
        env = Envelope('sender@example.com', ['rcpt@example.com'])
        envelope_raw = cPickle.dumps(env)
        self.storage.redis.hmget('test:asdf', 'envelope', 'attempts').AndReturn((envelope_raw, 13))
        self.mox.ReplayAll()
        get_env, attempts = self.storage.get('asdf')
        self.assertEqual(vars(env), vars(get_env))
        self.assertEqual(13, attempts)

    def test_load(self):
        self.storage.redis.keys('test:*').AndReturn(['test:one', 'test:two', 'test:three'])
        self.storage.redis.hget('test:one', 'timestamp').AndReturn(123)
        self.storage.redis.hget('test:two', 'timestamp').AndReturn(456)
        self.storage.redis.hget('test:three', 'timestamp').AndReturn(789)
        self.mox.ReplayAll()
        expected = [(123, 'one'), (456, 'two'), (789, 'three')]
        self.assertEqual(expected, list(self.storage.load()))

    def test_remove(self):
        self.storage.redis.delete('test:asdf')
        self.mox.ReplayAll()
        self.storage.remove('asdf')

    def test_notify(self):
        self.mox.ReplayAll()
        self.storage.notify('asdf', 0.0)

    def test_wait(self):
        ret = cPickle.dumps((1234567890, 'asdf'))
        self.storage.redis.blpop(['test:queue'], 0).AndReturn(('test:queue', ret))
        self.mox.ReplayAll()
        self.assertEqual((1234567890, 'asdf'), self.storage.wait())

    def test_wait_none(self):
        self.storage.redis.blpop(['test:queue'], 0).AndReturn(None)
        self.mox.ReplayAll()
        self.assertIsNone(self.storage.wait())


# vim:et:fdm=marker:sts=4:sw=4:ts=4
