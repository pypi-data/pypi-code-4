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

import Queue as queue
import collections
import sys
import time
import subprocess
import threading


_BUFFER_SIZE = 500


class LoggedProcess:
    def __init__(self, args, shell=False):
        self._args = args
        self._shell = shell
        self._log_file = None
        self._io_queue = queue.Queue()
        self._buffer_queue = collections.deque()
        self._open_streams = []

    def _stream_watcher(self, name, stream):
        for line in iter(stream.readline, b""):
            self._io_queue.put((name, line))

        stream.close()

        self._io_queue.put((name, None))

        if name in self._open_streams:
            self._open_streams.remove(name)

    def _queue_logger(self):
        streams = self._open_streams
        while len(streams) > 0:
            try:
                name, line = self._io_queue.get(True, 1)
            except queue.Empty:
                continue

            if line is None:
                if name in streams:
                    streams.remove(name)
            else:
                decoded_line = line.decode("utf-8")

                logging.info(decoded_line[:-1])

                self._buffer_queue.append(decoded_line)
                if len(self._buffer_queue) > _BUFFER_SIZE:
                    self._buffer_queue.popleft()

    def _cleanup(self):
        for name in self._open_streams:
            self._io_queue.put((name, None))

        self._logger.join()
        self._logger = None

        if self._log_file:
            self._log_file.close()
        self._log_file = None

    def _read_log(self, watch_log):
        if self._log_file is None:
            try:
                self._log_file = open(watch_log)
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
            self._command = self._args
        else:
            self._command = " ".join(self._args)

        logging.info("Running: %s" % self._command)

        self._process = subprocess.Popen(self._args,
                                         stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE,
                                         universal_newlines=True,
                                         shell=self._shell)

        watcher = threading.Thread(target=self._stream_watcher,
                                   args=("stdout", self._process.stdout))
        watcher.start()

        watcher = threading.Thread(target=self._stream_watcher,
                                   args=("stderr", self._process.stderr))
        watcher.start()

        self._logger = threading.Thread(target=self._queue_logger)
        self._logger.start()

        self._open_streams = ["stdout", "stderr"]

    def terminate(self):
        self._process.terminate()
        self._cleanup()

    def wait(self, watch_log=None, print_error=True):
        try:
            result = None
            while result is None:
                result = self._process.poll()
                if watch_log is not None:
                    self._read_log()
                time.sleep(0.1)
        except KeyboardInterrupt:
            self._cleanup()
            raise

        if watch_log:
            while True:
                if not self._read_log():
                    break

        self._cleanup()

        if print_error and result != 0:
            sys.stderr.write("\nCommand failed: %s\n\n" % self._command)
            for line in self._buffer_queue:
                sys.stderr.write(line)

        return result
