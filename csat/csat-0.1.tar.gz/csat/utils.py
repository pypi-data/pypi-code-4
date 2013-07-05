import argparse
import os
import sys
import signal
import time
import subprocess

from twisted.python.runtime import platformType
if platformType == "win32":
    from twisted.scripts._twistw import (
        ServerOptions,
        WindowsApplicationRunner as _SomeApplicationRunner
    )
else:
    from twisted.scripts._twistd_unix import (
        ServerOptions,
        UnixApplicationRunner as _SomeApplicationRunner
    )


def run_twistd(options):
    config = ServerOptions()
    config.parseOptions(options)
    _SomeApplicationRunner(config).run()


def django_cmd(envdir, cmd):
    cmd = ['django-admin.py'] + cmd + [
        '--settings=csat.webapp.settings',
        '--pythonpath={}'.format(envdir),
    ]
    os.environ['CSAT_ENVDIR'] = envdir
    return subprocess.check_output(cmd, env=os.environ)


class StopAction(argparse.Action):
    timeout = 5
    interval = 0.2

    @classmethod
    def add_to_parser(cls, parser, default_location):
        parser.add_argument('-s', '--stop', action=cls,
                            default=default_location, metavar='PIDFILE',
                            nargs='?')

    def __call__(self, parser, namespace, values, option_string=None):
        base = getattr(namespace, 'envdir', '.')
        self.pidfile = values or os.path.join(base, self.default)

        pid = self.getpid()
        if not self.term(pid, self.timeout):
            self.writeln('Process did not exit after {} seconds, killing!'.format(
                self.timeout))
            self.kill(pid)
            try:
                os.remove(self.pidfile)
            except OSError as e:
                if e.errno != 2:
                    raise
        sys.exit(0)

    def write(self, s):
        sys.stdout.write(s)
        sys.stdout.flush()

    def writeln(self, s):
        self.write(s + '\n')

    def kill(self, pid):
        try:
            os.kill(pid, signal.SIGKILL)
        except Exception as e:
            self.writeln('Could not kill process: {}'.format(e))
            sys.exit(1)

    def term(self, pid, timeout=5):
        try:
            os.kill(pid, signal.SIGTERM)
        except OSError as e:
            if e.errno == 3:
                self.writeln('Process is not running, removing stale pidfile.')
                os.remove(self.pidfile)
                return True
            else:
                raise
        else:
            self.write('TERM signal sent to PID {}, waiting for process to exit...'.format(pid))
            while timeout > 0:
                time.sleep(self.interval)
                try:
                    os.kill(pid, 0)
                except:
                    self.writeln(' DONE')
                    return True
                else:
                    self.write('.')
                    timeout -= self.interval
            else:
                self.writeln('')
                return False


    def getpid(self):
        try:
            try:
                with open(self.pidfile) as fh:
                    return int(fh.read().strip())
            except IOError as e:
                if e.errno == 2:
                    self.writeln('PID file ({}) not found.'.format(self.pidfile))
                else:
                    raise
        except:
            self.writeln('Could not read server PID from {}.'.format(self.pidfile))

        sys.exit(1)
