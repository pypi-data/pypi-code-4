#!/usr/bin/env python3
"""
Module ReadWriteMonitor
Sub-Package IO.CLASSES of Package PLIB3
Copyright (C) 2008-2013 by Peter A. Donis

Released under the GNU General Public License, Version 2
See the LICENSE and README files for more information

This module contains the ReadWriteMonitor class. This is
a useful class for testing client/server I/O channels; it
prints notification of all significant read/write method
calls to standard output, along with diagnostic info on
important state variables.
"""


class ReadWriteMonitor(object):
    
    def _delimiter(self):
        print("-" * 40)
    
    def handle_connect(self):
        print("{} handling connect".format(self.__class__.__name__))
        super(ReadWriteMonitor, self).handle_connect()
    
    def readable(self):
        result = super(ReadWriteMonitor, self).readable()
        print("{} readable: {}".format(self.__class__.__name__, result))
        return result
    
    def _read_data_monitor(self):
        print("{} read data {!r}".format(
            self.__class__.__name__, self.read_data))
        print("{} shutdown received: {}".format(
            self.__class__.__name__, self.shutdown_received))
        print("{} channel closed: {}".format(
            self.__class__.__name__, self.channel_closed()))
    
    def _read_flag_monitor(self):
        if hasattr(self, 'terminator_received'):
            print("{} terminator received: {}".format(
                self.__class__.__name__, self.terminator_received))
        if hasattr(self, 'read_len'):
            print("{} bytes expected: {}".format(
                self.__class__.__name__, self.read_len))
        if hasattr(self, 'bytes_read'):
            print("{} bytes read: {}".format(
                self.__class__.__name__, self.bytes_read))
    
    def handle_read(self):
        self._delimiter()
        self._read_data_monitor()
        self._read_flag_monitor()
        print("{} handling read".format(self.__class__.__name__))
        super(ReadWriteMonitor, self).handle_read()
        self._read_data_monitor()
        self._read_flag_monitor()
        self._delimiter()
    
    def read_complete(self):
        result = super(ReadWriteMonitor, self).read_complete()
        print("{} read complete: {}".format(
            self.__class__.__name__, result))
        return result
    
    def process_data(self):
        print("{} processing data {!r}".format(
            self.__class__.__name__, self.read_data))
        super(ReadWriteMonitor, self).process_data()
    
    def clear_read(self):
        self._delimiter()
        self._read_flag_monitor()
        print("{} clearing read data".format(self.__class__.__name__))
        super(ReadWriteMonitor, self).clear_read()
        self._read_flag_monitor()
        self._delimiter()
    
    def start(self, data):
        print("{} starting data {!r}".format(
            self.__class__.__name__, data))
        super(ReadWriteMonitor, self).start(data)
    
    def writable(self):
        result = super(ReadWriteMonitor, self).writable()
        print("{} writable: {}".format(
            self.__class__.__name__, result))
        return result
    
    def _write_data_monitor(self):
        print("{} write data {!r}".format(
            self.__class__.__name__, self.write_data))
    
    def _write_flag_monitor(self):
        if hasattr(self, 'terminator_written'):
            print("{} terminator written: {}".format(
                self.__class__.__name__, self.terminator_written))
        if hasattr(self, 'formatted'):
            print("{} formatted: {}".format(
                self.__class__.__name__, self.formatted))
    
    def handle_write(self):
        self._delimiter()
        self._write_data_monitor()
        self._write_flag_monitor()
        print("{} handling write".format(self.__class__.__name__))
        super(ReadWriteMonitor, self).handle_write()
        self._write_data_monitor()
        self._write_flag_monitor()
        self._delimiter()
    
    def write_complete(self):
        result = super(ReadWriteMonitor, self).write_complete()
        print("{} write complete: {}".format(
            self.__class__.__name__, result))
        return result
    
    def clear_write(self):
        self._delimiter()
        self._write_flag_monitor()
        print("{} clearing write data".format(self.__class__.__name__))
        super(ReadWriteMonitor, self).clear_write()
        self._write_flag_monitor()
        self._delimiter()
    
    def check_done(self):
        print("{} done: {}".format(
            self.__class__.__name__, self.done))
        super(ReadWriteMonitor, self).check_done()
        print("{} done: {}".format(
            self.__class__.__name__, self.done))
    
    def handle_error(self):
        print("{} handling error".format(self.__class__.__name__))
        super(ReadWriteMonitor, self).handle_error()
    
    def handle_close(self):
        print("{} handling close".format(self.__class__.__name__))
        super(ReadWriteMonitor, self).handle_close()
