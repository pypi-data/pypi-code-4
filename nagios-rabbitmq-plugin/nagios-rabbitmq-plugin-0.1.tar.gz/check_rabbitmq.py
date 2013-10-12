#!/usr/bin/env python

import argparse, logging, nagiosplugin, requests, urllib

class QueueMetric(nagiosplugin.Resource):
    def __init__(self, hostname, port, username, password, queue, vhost, timeout):
        self.rabbitmq_url = 'http://%s:%s' % (hostname, port)
        self.rabbitmq_auth = (username, password)
        self.queue = queue
        self.vhost = vhost
        self.timeout = float(timeout)
        
    def check_overview(self):
        r = requests.get('%s/api/overview' % self.rabbitmq_url, auth=self.rabbitmq_auth)
        result = r.json()
        total = result.get('queue_totals').get('messages')
        return [nagiosplugin.Metric('Msgs Queued', total, '/total')]
    
    def check_queue(self):
        r = requests.get('%s/api/queues/%s/%s' % (self.rabbitmq_url, urllib.quote_plus(self.vhost), self.queue), auth=self.rabbitmq_auth)
        result = r.json()
        total = result.get('messages')
        return [nagiosplugin.Metric('Msgs Queued', total, '/%s' % self.queue)]
        
        
    def probe(self):
        if self.queue:
            return self.check_queue()
        else:
            return self.check_overview()
        
@nagiosplugin.guarded
def main():
    
    argp = argparse.ArgumentParser(description='Nagios plugin to check RabbitMQ queue health')
    
    argp.add_argument('-H', '--hostname', default='localhost',
                      help='hostname/ip for rabbitmq server')
    argp.add_argument('-P', '--port', default=55672,
                      help='port to connect to rabbitmq server')
    argp.add_argument('-u', '--username', default='guest',
                      help='auth: username')
    argp.add_argument('-p', '--password', default='',
                      help='auth: password')
    argp.add_argument('-Q', '--queue', default=False,
                      help='queue to check')
    argp.add_argument('-V', '--vhost', default='/',
                      help='vhost queue belongs to')
    argp.add_argument('-w', '--warning', metavar='RANGE', default='0:',
                      help='warning if number of messages is outside RANGE')
    argp.add_argument('-c', '--critical', metavar='RANGE', default='0:',
                      help='critical if number of messages is outside RANGE')
    argp.add_argument('-v', '--verbose', action='count', default=0,
                      help='increase verbosity (use up to 3 times)')
    argp.add_argument('-t', '--timeout', default=10,
                      help='abort execution after TIMEOUT seconds')
    
    args=argp.parse_args()
    check = nagiosplugin.Check(
            QueueMetric(args.hostname, args.port, args.username, args.password, args.queue, args.vhost, args.timeout),
            nagiosplugin.ScalarContext('Msgs Queued', args.warning, args.critical)
            )
    check.main(verbose=args.verbose)

if __name__ == "__main__":
    main()