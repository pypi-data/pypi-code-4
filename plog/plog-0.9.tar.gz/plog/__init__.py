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

import sys
import time
import subprocess
import threading


class LoggedProcess:
    def __init__(self, args, watch_log=None, shell=False):
        self._args = args
        self._shell = shell
        self._watch_log = watch_log
        self._log_file = None

    def _stream_watcher(self, io_queue, name, stream):
        for line in iter(stream.readline, b""):
            io_queue.put((name, line))

        stream.close()

        io_queue.put((name, None))

    def _queue_logger(self, io_queue, stream_names):
        while len(stream_names) > 0:
            try:
                name, line = io_queue.get(True, 1)
            except queue.Empty:
                continue

            if line is None:
                stream_names.remove(name)
            else:
                logging.info(line.decode("utf-8")[:-1])

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
        process = subprocess.Popen(self._args,
                                   stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE,
                                   universal_newlines=True,
                                   shell=self._shell)

        io_queue = queue.Queue()

        streams = {"stdout": process.stdout,
                   "stderr": process.stderr}

        for name, stream in streams.items():
            watcher = threading.Thread(target=self._stream_watcher,
                                       args=(io_queue, name, stream))
            watcher.start()

        self._logger = threading.Thread(target=self._queue_logger,
                                        args=(io_queue, list(streams.keys())))
        self._logger.start()

        try:
            result = None
            while result is None:
                result = process.poll()
                self._read_log()
                time.sleep(0.1)
        except KeyboardInterrupt:
            for name in streams.keys():
                io_queue.put((name, None))
            self._cleanup()
            raise

        while True:
            if not self._read_log():
                break

        self._cleanup()

        return result


def check_run(args, shell=False):
    returncode = run(args, shell)
    if returncode != 0:
        raise subprocess.CalledProcessError(returncode, args)


def run(args, shell=False):
    logging.info(args)

    logged_process = LoggedProcess(args, shell=shell)
    process = logged_process.execute()

    return process.returncode
