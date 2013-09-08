#!/usr/bin/env python

"""
A Darner client library.
"""

from collections import defaultdict
import re
import memcache


class Client(object):
    """darner queue client."""

    def __init__(self, servers):
        """Constructor.

        :param servers: The list of servers to connect to, really should only
            be one for a darner client;
        :type servers: list
        :type queue: string

        """

        self.__memcache = DarnerClient(servers=servers)
        #self.queue = queue

    def add(self, queue, data, expire=None):
        """Add a job onto the queue.

        WARNING:  You should only send strings through to the queue, if not
        the python-memcached library will serialize these objects and since
        darner ignores the flags supplied during a set operation, when the
        object is retrieved from the queue it will not be unserialized.

        :param data: The job itself
        :type data: mixed
        :param expire: The expiration time of the job, if a job doesn't get
            used in this amount of time, it will silently die away.
        :type expire: int
        :queue: the queue we want to add data into
        :return: True/False
        :rtype: bool

        """

        if expire is None:
            expire = 0

        ret = self.__memcache.set(queue, data, expire)

        if ret == 0:
            return False

        return True

    def get(self, queue, timeout=None):
        """Get a job off the queue. (unreliable)

        :param timeout: The time to wait for a job if none are on the queue
            when the initial request is made. (seconds)
        :type timeout: int
        :return: The job
        :rtype: mixed

        """

        cmd = '%s' % (queue)

        if timeout is not None:
            cmd = '%s/t=%d' % (cmd, timeout)

        return self.__memcache.get('%s' % (cmd))

    def next(self, queue, timeout=None):
        """Marks the last job as compelete and gets the next one.

        :param timeout: The time to wait for a job if none are on the queue
            when the initial request is made. (seconds)
        :type timeout: int
        :return: The job
        :rtype: mixed

        """

        cmd = '%s/close' % (queue)

        if timeout is not None:
            cmd = '%s/t=%d' % (cmd, timeout)

        return self.__memcache.get('%s/open' % (cmd))

    def peek(self, queue, timeout=None):
        """Copy a job from the queue, leaving the original in place.

        :param timeout: The time to wait for a job if none are on the queue
            when the initial request is made. (seconds)
        :type timeout: int
        :return: The job
        :rtype: mixed

        """

        cmd = '%s/peek' % (queue)

        if timeout is not None:
            cmd = '%s/t=%d' % (cmd, timeout)

        return self.__memcache.get(cmd)

    def abort(self, queue):
        """Mark a job as incomplete, making it available to another client.

        :return: True on success
        :rtype: boolean

        """

        self.__memcache.get('%s/abort' % (queue))
        return True

    def finish(self, queue):
        """Mark the last job read off the queue as complete on the server.

        :return: True on success
        :rtype: bool

        """

        self.__memcache.get('%s/close' % (queue))
        return True

    def delete(self, queue):
        """Delete this queue from the darner server.

        :return: True on success, False on error
        :rtype: bool

        """

        ret = self.__memcache.delete(queue)

        if ret == 0:
            return False

        return True

    def close(self):
        """Force the client to disconnect from the server.

        :return: True
        :rtype: bool

        """

        self.__memcache.disconnect_all()
        return True

    def flush(self, queue):
        """Clear out (remove all jobs) in the current self.queue.

        :return: True
        :rtype: bool

        """

        self.__memcache.flush(queue)
        return True

    def flush_all(self):
        """Clears out all jobs in all the queues on this darner server.

        :return: True
        :rtype: bool

        """

        self.__memcache.flush_all()
        return True

    def reload(self):
        """Forces the darner server to reload the config.

        :return: True
        :rtype: bool

        """

        self.__memcache.reload()
        return True

    def stats(self):
        """Get the stats from the server and parse the results into a python
           dict.

           {
               '127.0.0.1:22133': {
                   'stats': {
                       'cmd_get': 10,
                       ...
                   },
                   'queues': {
                       'queue_name': {
                           'age': 30,
                           ...
                       }
                   }
               }
           }
        """

        server = None
        _sstats = {}
        _qstats = {}

        for server, stats in self.raw_stats():
            server = server.split(' ', 1)[0]
            for name, stat in stats.iteritems():
                if not name.startswith('queue_'):
                    try:
                        _sstats[name] = long(stat)
                    except ValueError:
                        _sstats[name] = stat

        for name, stats in re.findall('queue \'(?P<name>.*?)\' \{(?P<stats>.*?)\}', self.raw_stats(True), re.DOTALL):
            _stats = {}
            for stat in [stat.strip() for stat in stats.split('\n')]:
                if stat.count('='):
                    (key, value) = stat.split('=')
                    _stats[key] = long(value)
            _qstats[name] = _stats

        if server is None:
            return None

        return (server, dict([('server', _sstats), ('queues', _qstats)]))

    def raw_stats(self, pretty=None):
        """Get statistics in either the pretty (darner) format or the
        standard memcache format.

        :param pretty: Set to True to generate the stats in the darner/pretty
            format.
        :type pretty: bool
        :return: The stats text blob, or the structed format from the
            underlying memcache library
        :rtype: string

        """

        if pretty is True:
            return self.__memcache.pretty_stats()

        return self.__memcache.get_stats()

    def shutdown(self):
        """Shutdown the darner server gracefully.

        :return: None
        :rtype: None

        """

        return self.__memcache.shutdown()

    def version(self):
        """Get the version for the darner server.

        :return: The darner server version. e.g. 1.2.3
        :rtype: string

        """

        return self.__memcache.version()


class DarnerClient(memcache.Client):
    """Darner Memcache Client.
    """

    def reload(self):
        for s in self.servers:
            if not s.connect(): continue
            s.send_cmd('RELOAD')
            s.expect('OK')

    def flush(self, key):
        for s in self.servers:
            if not s.connect(): continue
            s.send_cmd('FLUSH %s' % (key))
            s.expect('OK')

    def pretty_stats(self):
        return self.__read_cmd('DUMP_STATS')

    def version(self):
        data = []
        for s in self.servers:
            if not s.connect(): continue
            s.send_cmd('VERSION')
            data.append(s.readline())

        return ('\n').join(data).split(' ', 1)[1]

    def shutdown(self):
        for s in self.servers:
            if not s.connect(): continue
            s.send_cmd('SHUTDOWN')

    def __read_cmd(self, cmd):
        data = []
        for s in self.servers:
            if not s.connect(): continue
            s.send_cmd(cmd)
            data.append(self.__read_string(s))

        return ('\n').join(data)

    def __read_string(self, s):
        data = []
        while True:
            line = s.readline()
            if not line or line.strip() == 'END': break
            data.append(line)

        return ('\n').join(data)
