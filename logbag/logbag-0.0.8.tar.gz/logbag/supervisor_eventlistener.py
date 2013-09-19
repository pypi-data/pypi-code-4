#!/usr/bin/env python

import argparse
import os
import sys
from supervisor import childutils


try:
    from logbag import Logger
except ImportError:
    here = os.path.abspath(os.path.dirname(__file__))
    sys.path.insert(1, os.path.join(here, os.pardir))
    from logbag import Logger


EVENTS = (
    'PROCESS_STATE',
    'PROCESS_STATE_STARTING',
    'PROCESS_STATE_RUNNING',
    'PROCESS_STATE_BACKOFF',
    'PROCESS_STATE_STOPPING',
    'PROCESS_STATE_EXITED',
    'PROCESS_STATE_STOPPED',
    'PROCESS_STATE_FATAL',
    'PROCESS_STATE_UNKNOWN',
    'REMOTE_COMMUNICATION',
    'PROCESS_LOG',
    'PROCESS_LOG_STDOUT',
    'PROCESS_LOG_STDERR',
    'PROCESS_COMMUNICATION',
    'PROCESS_COMMUNICATION_STDOUT',
    'PROCESS_COMMUNICATION_STDERR',
    'SUPERVISOR_STATE_CHANGE',
    'SUPERVISOR_STATE_CHANGE_RUNNING',
    'SUPERVISOR_STATE_CHANGE_STOPPING',
)


DEFAULT_EVENT_LEVELS = {
    'PROCESS_STATE_FATAL': 'critical',
    'PROCESS_STATE_UNKNOWN': 'error',
    'PROCESS_LOG_STDERR': 'error',
    'PROCESS_COMMUNICATION_STDERR': 'error',
    'PROCESS_STATE_BACKOFF': 'warning',
    'PROCESS_STATE_EXITED': 'warning',
    'PROCESS_STATE_RUNNING': 'info',
    'PROCESS_STATE_STOPPED': 'info',
    'SUPERVISOR_STATE_CHANGE_RUNNING': 'info',
    'SUPERVISOR_STATE_CHANGE_STOPPING': 'info',
}


class SupervisorEventListener:
    def __init__(self, url, user, log, event_levels=None):
        self.stdin = sys.stdin
        self.stdout = sys.stdout
        self.stderr = sys.stderr
        self.event_levels = event_levels or DEFAULT_EVENT_LEVELS
        self.log = Logger(url, user, log)

    def runforever(self):
        while 1:
            headers, payload = childutils.listener.wait(self.stdin, self.stdout)
            event = headers['eventname']
            level = self.event_levels.get(event)
            if level:
                self.log.log(level, payload, type='supervisor', event=event)
            childutils.listener.ok(self.stdout)


def main():
    if not 'SUPERVISOR_SERVER_URL' in os.environ:
        sys.stderr.write('Script must be run as a supervisor event listener\n')
        sys.stderr.flush()
        return sys.exit(1)
    parser = argparse.ArgumentParser()
    parser.add_argument('url', help='logbag url')
    parser.add_argument('user', help='logbag user')
    parser.add_argument('log', help='logbag log')
    choices = ('debug', 'info', 'warning', 'error', 'critical')
    for event in EVENTS:
        parser.add_argument('--%s' % event, choices=choices)
    args = parser.parse_args()
    event_levels = {}
    for event in EVENTS:
        level = getattr(args, event)
        if level:
            event_levels[event] = level
    listener = SupervisorEventListener(args.url, args.user, args.log, event_levels=event_levels)
    listener.runforever()


if __name__ == '__main__':
    main()
