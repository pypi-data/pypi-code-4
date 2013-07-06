import argparse
import os

from twisted.python.filepath import FilePath

from csat.utils import StopAction, run_twistd


PIDFILE = os.environ.get('CSAT_PIDFILE', 'csat-collect.pid')
LOGFILE = os.environ.get('CSAT_LOGFILE', 'csat-collect.log')

_endpoints = {}


def main():
    parser = argparse.ArgumentParser('csat-acquisition-server')
    parser.add_argument('-n', '--nodaemon', action='store_false',
                        dest='daemonize')

    parser.add_argument('-p', '--public', metavar='ENDPOINT',
                        default='tcp:7002')
    parser.add_argument('-r', '--private', metavar='ENDPOINT',
                        default='tcp:7001:interface=127.0.0.1')

    parser.add_argument('-s', '--stop', action=StopAction, default=PIDFILE,
                        nargs='?')

    args = parser.parse_args()

    server_module = FilePath(__file__).parent().sibling('server.py')
    options = [
        '-y', server_module.path,
    ]
    if args.daemonize:
        options += [
            '--pidfile', PIDFILE,
            '--logfile', LOGFILE,
        ]
    else:
        options += [
            '-n',
            '--pidfile=',
        ]

    _endpoints['public'] = args.public
    _endpoints['private'] = args.private

    run_twistd(options)


if __name__ == '__main__':
    main()
