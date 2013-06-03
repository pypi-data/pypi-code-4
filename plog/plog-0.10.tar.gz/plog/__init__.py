# Copyright 2013 Daniel Narvaez
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#   http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging

try:
    import queue
except ImportError:
    import Queue as queue

import collections
import sys
import time
import subprocess
import threading


_BUFFER_SIZE = 500


class LoggedProcess:
    def __init__(self, args, watch_log=None, shell=False):
        self._args = args
        self._shell = shell
        self._watch_log = watch_log
        self._log_file = None
        self._io_queue = queue.Queue()
        self._buffer_queue = collections.deque()

    def _stream_watcher(self, name, stream):
        for line in iter(stream.readline, b""):
            self._io_queue.put((name, line))

        stream.close()

        self._io_queue.put((name, None))

    def _queue_logger(self):
        streams = ["stdout", "stderr"]
        while len(streams) > 0:
            try:
                name, line = self._io_queue.get(True, 1)
            except queue.Empty:
                continue

            if line is None:
                streams.remove(name)
            else:
                decoded_line = line.decode("utf-8")

                logging.info(decoded_line[:-1])

                self._buffer_queue.append(decoded_line)
                if len(self._buffer_queue) > _BUFFER_SIZE:
                    self._buffer_queue.popleft()

    def _cleanup(self):
        self._logger.join()
        self._logger = None

        if self._log_file:
            self._log_file.close()
        self._log_file = None

    def _read_log(self):
        if self._watch_log is None:
            return

        if self._log_file is None:
            try:
                self._log_file = open(self._watch_log)
            except IOError:
                pass

        if self._log_file:
            data = self._log_file.read(8192)
            if data:
                sys.stdout.write(data)
                return True
            else:
                return False

    def execute(self):
        if isinstance(self._args, basestring):
            command = self._args
        else:
            command = " ".join(self._args)

        logging.info("Running: %s" % command)

        process = subprocess.Popen(self._args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True,
                                   shell=self._shell)

        watcher = threading.Thread(target=self._stream_watcher,
                                   args=("stdout", process.stdout))
        watcher.start()

        watcher = threading.Thread(target=self._stream_watcher,
                                   args=("stderr", process.stderr))
        watcher.start()

        self._logger = threading.Thread(target=self._queue_logger)
        self._logger.start()

        try:
            result = None
            while result is None:
                result = process.poll()
                self._read_log()
                time.sleep(0.1)
        except KeyboardInterrupt:
            for name in "stdout", "stderr":
                self._io_queue.put((name, None))
            self._cleanup()
            raise

        while True:
            if not self._read_log():
                break

        self._cleanup()

        if result != 0:
            sys.stderr.write("\nCommand failed: %s\n\n" % command)
            for line in self._buffer_queue:
                sys.stderr.write(line)

        return result


def check_run(args, shell=False):
    returncode = run(args, shell)
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, args)


def run(args, shell=False):
    logged_process = LoggedProcess(args, shell=shell)
    process = logged_process.execute()

    return process.returncode
