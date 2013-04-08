import Queue
from collections import deque
import getopt
from itertools import chain
import json
import logging
import os
from random import random
import re
import tempfile
from threading import Thread
from datetime import datetime, time, timedelta
from time import sleep, gmtime, strftime
import traceback
import sys
from threadpool import ThreadPool, NoResultsPending, WorkRequest, NoWorkersAvailable
import yaml
from dnslb.check import check_http


__author__ = 'leifj'


class Node(object):
    def __init__(self, hostname):
        self.hostname = hostname
        self.status = deque([], 5)

    def __str__(self):
        return "%s (%s)" % (self.hostname, ",".join("%s" % s[1] for s in self.status))

    def add_status(self, ok=True, reason=None, exc=None):
        self.status.appendleft([datetime.now(), ok, reason, exc])

    @property
    def ok(self):
        if not self.status:
            return False
        else:
            return self.status[0][1]


class Monitor(Thread):
    def __init__(self, hosts, mult=2, timeout=10, sleep_time=1):
        super(Monitor, self).__init__()
        self.num_hosts = len(hosts)
        self.num_workers = mult * self.size
        self.pool = ThreadPool(self.num_workers)
        self.nodes = {}
        for host in hosts:
            self.nodes[host] = Node(host)
        self.timeout = timeout
        self.running = True
        self.stop = False
        self.remaining = 0
        self.sleep_time = sleep_time
        self.num_started = 0
        self.num_fail = 0
        self.num_ok = 0
        self.num_flipped = 0
        self.start()

    def ok(self, hostname):
        return self.nodes[hostname].ok

    @property
    def num_processed(self):
        return self.num_ok + self.num_fail

    @property
    def size(self):
        return self.num_hosts

    def reset_flipped(self):
        self.num_flipped = 0

    def __str__(self):
        return "<Monitor " + ",".join(["%s" % n for n in self.nodes.values()]) + ">"

    def _test_result(self, req, res):
        self.remaining -= 1
        try:
            hostname = req.args[0]
            logging.debug("result for %s(%s): %s" % (hostname, req.callable, res))
            node = self.nodes[hostname]
            if res:
                self.num_ok += 1
                if not self.ok(hostname):
                    self.num_flipped += 1
                node.add_status(True)
            else:
                self.num_fail += 1
                if self.ok(hostname):
                    self.num_flipped += 1
                node.add_status(False, "check failed")
        except Exception, ex:
            logging.warning(ex)
            pass

    def _test_fail(self, req, exc_info):
        try:
            self.remaining -= 1
            logging.debug("_test_fail %s" % repr(req))
            traceback.print_exception(*exc_info)
            hostname = req.args[0]
            node = self.nodes[hostname]
            self.num_fail += 1
            if self.ok(hostname):
                self.num_flipped += 1
            node.add_status(False, "caught exception", exc_info)
        except Exception, ex:
            logging.warning(ex)
            pass

    def schedule(self, check_callable, **kwargs):
        for node in self.nodes.values():
            req = WorkRequest(check_callable,
                              [node.hostname],
                              kwds=kwargs,
                              callback=self._test_result,
                              exc_callback=self._test_fail)
            try:
                logging.debug("adding new request for %s on %s using %s" % (check_callable, node.hostname, kwargs))
                self.pool.putRequest(req, timeout=self.timeout)
                self.num_started += 1
                self.remaining += 1
            except Queue.Full:
                logging.warning("Unable to schedule service check for %s (queue full)." % node.hostname)

    def halt(self):
        self.running = False
        self.join()

    def shutdown(self):
        self.stop = True
        self.join()

    def wait(self):
        if self.pool.workRequests:
            self.pool.wait()

    def run(self):
        logging.info("Starting up!"
                     "")
        while self.running:
            try:
                if self.stop:
                    logging.debug("waiting for all %d remaining tasks..." % self.remaining)
                    self.pool.wait()
                    logging.debug("now %d" % self.remaining)
                    if self.remaining == 0:
                        self.running = False
                else:
                    self.pool.poll(block=False)
            except KeyboardInterrupt:
                logging.info("Shutting down...")
                self.stop = True
            except NoResultsPending:
                sleep(self.sleep_time)
                pass
            except Exception, ex:
                logging.error(ex)
        if self.stop:
            assert (self.remaining == 0)
        self.pool.dismissWorkers(self.num_workers, do_join=True)
        return True

    def dns_zone(self, config):
        """

        :param config:
        :return: :raise:
        """
        zone = dict()
        zone['ttl'] = 120
        zone['serial'] = int(strftime("%Y%M%d00", gmtime()))
        zone['contact'] = config['contact']
        zone['max_hosts'] = 2

        ns = dict()
        for n in config['nameservers']:
            ns[n] = None
        zone['data'] = {'': {'ns': ns}}

        def _add_addr(ip, cn_a):
            if '.' in ip:
                cn_a['a'].append([ip, "100"])
            elif ':' in ip:
                cn_a['aaaa'].append([ip, "100"])
            else:
                raise Exception("Unknown address format %s" % ip)

        for v in config['aliases']:
            zone['data'][v] = dict(alias="")

        for ln in config['labels'].keys():
            zone['data'][ln] = dict(a=[], aaaa=[])

        vn_a = dict(a=[],aaaa=[])
        for cn in config['hosts'].keys():
            zone['data'].setdefault(cn, {})

            zone['data'][cn] = dict(a=[], aaaa=[])
            for ip in config['hosts'][cn]:
                _add_addr(ip, zone['data'][cn])
                if self.ok(ip):
                    _add_addr(ip, vn_a)
                    for ln in config['labels']:
                        if cn in config['labels'][ln]:
                            _add_addr(ip, zone['data'][ln])
                else:
                    logging.warn("Excluding (%s) %s - not ok" % (cn, ip))

        if len(vn_a['a']) > 0:
            zone['data']['']['a'] = vn_a['a']

        if len(vn_a['aaaa']) > 0:
            zone['data']['']['aaaa'] = vn_a['aaaa']

        return zone


def safe_write(fn, data):
    tmpn = None
    try:
        dirname, basename = os.path.split(fn)
        with tempfile.NamedTemporaryFile('w', delete=False, prefix=".%s" % basename, dir=dirname) as tmp:
            tmp.write(data)
            tmpn = tmp.name
        if os.path.exists(tmpn) and os.stat(tmpn).st_size > 0:
            os.rename(tmpn, fn)
            return True
    except Exception, ex:
        logging.error(ex)
    finally:
        if tmpn is not None and os.path.exists(tmpn):
            try:
                os.unlink(tmpn)
            except Exception, ex:
                logging.warning(ex)
                pass
    return False


def _err(ec, msg):
    print msg
    print 'for help use --help'
    sys.exit(ec)


def tdelta(delta_str):
    """
Parse a time delta from expressions like 1w 32d 4h 5s - i.e in weeks, days hours and/or seconds.

:param delta_str: A human-friendly string representation of a timedelta
    """
    keys = ["weeks", "days", "hours", "minutes"]
    regex = "".join(["((?P<%s>\d+)%s ?)?" % (k, k[0]) for k in keys])
    kwargs = {}
    for k, v in re.match(regex, delta_str).groupdict(default="0").items():
        kwargs[k] = int(v)
    return timedelta(**kwargs)


def main():
    try:
        opts, args = getopt.getopt(sys.argv[1:], 'hz:c:M:A:',
                                   ['help', 'loglevel=', 'logfile=', 'zone', 'config', 'max-changes', 'max-age'])
    except getopt.error, msg:
        _err(2, msg)

    config_file = 'config.yaml'
    zone_file = 'zone.json'
    loglevel = 'INFO'
    logfile = None
    max_changes = 0
    max_age = "PT1H"
    for o, a in opts:
        if o in ('-h', '--help'):
            print __doc__
            sys.exit(0)
        elif o in '--loglevel':
            loglevel = getattr(logging, a.upper(), None)
            if not isinstance(loglevel, int):
                raise ValueError('Invalid log level: %s' % loglevel)
        elif o in '--logfile':
            logfile = a
        elif o in ('--config', '-c'):
            config_file = a
        elif o in ('--zone', '-z'):
            zone_file = a
        elif o in ('--max-change', '-M'):
            max_changes = a
        elif o in ('--max-age', '-A'):
            max_age = a

    log_args = {'level': loglevel}
    if logfile is not None:
        log_args['filename'] = logfile
    logging.basicConfig(**log_args)

    config = None
    if not os.path.exists(config_file):
        _err(1, "Configuration file does not exists: %s" % config_file)

    with open(config_file) as fd:
        config = yaml.safe_load(fd)

    def _num_addrs(zone):
        if zone is None:
            return 0
        if not 'data' in zone:
            return 0
        top = zone['data'].get('', None)
        if top is None:
            return 0
        return len(top.get("a", [])) + len(top.get("aaaa", []))

    max_age_delta = tdelta(max_age)

    mon = Monitor(list(chain.from_iterable(config['hosts'].values())), sleep_time=2)  # just monitor one address
    if max_changes == 0:
        max_changes = mon.size - 1

    while True:
        try:
            zone = None
            last_wrote_zone = datetime.now()
            for ch in config['checks']:
                for check_name, kwargs in ch.iteritems():
                    mon.schedule(getattr(check, check_name), **kwargs)
                sleep(10 * random())

            if mon.num_processed > mon.size:
                new_zone = mon.dns_zone(config)

                num_changes = _num_addrs(zone) - _num_addrs(new_zone)
                if num_changes < max_changes or last_wrote_zone > datetime.now() + max_age_delta:
                    zone = new_zone
                    logging.info("writing zone with %d top level addresses" % _num_addrs(zone))
                    safe_write(zone_file, json.dumps(zone))
                    last_wrote_zone = datetime.now()
                else:
                    logging.info("too many changes (%d > %d) - holding off write" % (num_changes, max_changes))

            sleep(60 * random())
        except KeyboardInterrupt:
            logging.info("Shutting down...")
            mon.halt()
            break
