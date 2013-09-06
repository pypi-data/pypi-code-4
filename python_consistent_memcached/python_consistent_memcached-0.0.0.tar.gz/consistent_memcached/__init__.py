from md5 import md5
from random import Random
from memcached import Cient as _Client


class Client(_Client):
    def _init_buckets(self):
        servers = [(server, server.weight) for server in self.servers]
        self.buckets = make_consistent_weighted_buckets(servers)


def make_consistent_weighted_buckets(weighted_machines, slots=16387*2+1):
    machines = []
    for machine, count in weighted_machines:
        machines.extend([machine]*count)
    return make_consistent_for_modulus(machines, slots)
    
 
def make_consistent_buckets(machines, slots=16387):

    # TODO(adam.depricne): Add warning here if there are too many
    # machines for the number of slots
    
    streams = build_streams(machines)
    counter = slots
    bucket = [None] * slots 
    while True:
        for stream, machine in zip(streams, machines):
            if counter <= 0: return bucket
            x = stream.randint(0, slots-1)
            while bucket[x]:
                x = stream.randint(0, slots-1)
            bucket[x] = machine
            counter -= 1 
    # Never reached


def build_streams(hosts):
    return [_Random(md5(host).hexdigest()) for host in hosts]


def _Random(key, _cache={}):
    # Memoizing randomizers allows us to avoid collisions between
    # duplciate keys when called from make_consistent_for_modulus
    if key in _cache:
        return _cache[key]
    _cache[key] = Random(key)
    return _cache[key]


