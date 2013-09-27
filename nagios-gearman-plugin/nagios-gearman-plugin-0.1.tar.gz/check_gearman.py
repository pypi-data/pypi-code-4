#!/usr/bin/env python

import argparse, logging, nagiosplugin, gearman

class GearmanWorkerMetric(nagiosplugin.Resource):
    def __init__(self, hostname, port, function, timeout):
        self.gearman_host = hostname + ':' + str(port)
        self.function = function
        self.timeout = float(timeout)
        
    def get_stats(self, task):
        gm_admin_client = gearman.GearmanAdminClient([self.gearman_host], self.timeout)
        stats = gm_admin_client.get_status()
        for stat in stats:
            if stat.get('task') == task:
                return stat
        return False
    
    def get_capacity(self, stats):
        workers = stats.get('workers')
        queued = stats.get('queued')
        if workers == 0 or queued > workers:
            return 100
        return round(((queued / float(workers)) * 100),2)
        
    def probe(self):
        func_stats = self.get_stats(self.function)
        if func_stats == False:
            return []
        return [nagiosplugin.Metric('Workers Avail', func_stats.get('workers'), ''),
                nagiosplugin.Metric('Workers Capacity', self.get_capacity(func_stats), '%')]
        
@nagiosplugin.guarded
def main():
    
    argp = argparse.ArgumentParser(description='Nagios plugin to check gearman worker availability and capacity')
    
    argp.add_argument('-H', '--hostname', default='localhost',
                      help='hostname/ip for gearman server')
    argp.add_argument('-p', '--port', default=4730,
                      help='port to connect to gearman server')
    argp.add_argument('-f', '--function', required=True,
                      help='function (queue) to check')
    argp.add_argument('-w', '--warning-avail', metavar='RANGE', default='0:',
                      help='warning if workers available is outside RANGE')
    argp.add_argument('-c', '--critical-avail', metavar='RANGE', default='0:',
                      help='critical if workers available is outside RANGE')
    argp.add_argument('-W', '--warning-cap', metavar='RANGE', default='75',
                      help='warning if workers capacity is outside RANGE')
    argp.add_argument('-C', '--critical-cap', metavar='RANGE', default='75',
                      help='critical if workers capacity is outside RANGE')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=10,
                      help='abort execution after TIMEOUT seconds')
    
    args=argp.parse_args()
    check = nagiosplugin.Check(
            GearmanWorkerMetric(args.hostname, args.port, args.function, args.timeout),
            nagiosplugin.ScalarContext('Workers Avail', args.warning_avail, args.critical_avail),
            nagiosplugin.ScalarContext('Workers Capacity', args.warning_cap, args.critical_cap)
            )
    check.main(verbose=args.verbose)

if __name__ == "__main__":
    main()