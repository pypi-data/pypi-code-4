#!/usr/bin/python
import os
import sys
import subprocess
import datetime
import ConfigParser

import common

if sys.platform == 'win32':
    process_config = ConfigParser.ConfigParser()
    process_config.read(common.config_files('paths_win.ini'))
    os.environ['PATH'] = ';'.join([value for key, value in process_config.items('paths')]) + ';' + os.environ['PATH']

class _Process(object):
    def __init__(self):
        self.log_file = None
        self.total_duration = datetime.timedelta()

    def __del__(self):
        if self.log_file:
            self.log_file.write('#TOTAL DURATION: %s\n' % (self._format_duration(self.total_duration)))

    @staticmethod
    def _format_duration(duration):
        total_seconds = round(duration.total_seconds())
        hours, remainder = divmod(total_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        if hours > 0:
            return "%dh%dm%ds" % (hours, minutes, seconds)
        elif minutes > 0:
            return "%dm%ds" % (minutes, seconds)
        else:
            return "%ds" % (seconds)

    def execute(self, command, excepted_error_code=0):
        if self.log_file:
            self.log_file.write(command + '\n')

        start_time = datetime.datetime.now()
        ret = subprocess.call(command, shell=True)
        duration = datetime.datetime.now() - start_time
        self.total_duration += duration

        if self.log_file:
            self.log_file.write('#%s\n\n' % (self._format_duration(duration)))
            self.log_file.flush()
        if excepted_error_code is not None and ret != excepted_error_code:
            raise subprocess.CalledProcessError(ret, command)

    def execute_as_generator(self, command, excepted_error_code=0):
        if self.log_file:
            self.log_file.write(command + '\n')

        start_time = datetime.datetime.now()
        p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
        for line in iter(p.stdout.readline, ''):
            yield line
        duration = datetime.datetime.now() - start_time
        self.total_duration += duration

        if self.log_file:
            self.log_file.write('#%s\n\n' % (self._format_duration(duration)))
            self.log_file.flush()

        ret = p.wait()
        if excepted_error_code is not None and ret != excepted_error_code:
            raise subprocess.CalledProcessError(p.returncode, command)

    def reset_log(self, log_fname):
        if self.log_file:
            self.log_file.write('#TOTAL DURATION: %s\n' % (self._format_duration(self.total_duration)))
            self.total_duration = datetime.timedelta()
        self.log_file = open(log_fname, 'w')

_process = _Process()

def Process(): return _process

if __name__ == '__main__':
    process = Process()
    process.reset_log('test.log')
    for line in process.execute_as_generator('ping -c 3 code.google.com'):
        pass
