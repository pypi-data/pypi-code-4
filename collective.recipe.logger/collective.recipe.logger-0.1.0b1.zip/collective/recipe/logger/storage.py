""" The module provides storage for logs """

import csv
import json
import os
import pickle
import shutil
import logging
from itertools import imap
from collections import deque


def csv_serialization(obj):
    # TODO: write an object serializer.
    #  For now it detects a bad object.
    logging.error(
        'The object format is not appropriate.\n'
        'The object type is: %s' % obj.__class__.__name__
    )


class PersistentDeque(deque):
    """ Persistent deque with an API compatible with shelve and anydbm.

    The deque is kept in memory.

    Write to disk is delayed until close or sync (similar to gdbm's fast mode).

    Input file file format is automatically discovered.
    Output file format is selectable between pickle, json, and csv.
    All three serialization formats are backed by fast C implementations.

    """

    def __init__(
            self, mode=None,
            file_format='json', home_dir='.', maxlen=None,
            *args, **kwds
    ):
        deque.__init__(self, *args, **kwds)
        self.mode = mode         # None or an octal triple like 0644
        self.file_format = file_format     # 'csv', 'json', or 'pickle'
        self.home_dir = home_dir

    def dump(self, fileobj):
        if self.file_format == 'csv':
            writer = csv.writer(fileobj)
            writer.writerows(imap(lambda x: x.items(), self))
        elif self.file_format == 'json':
            json.dump(
                list(self),
                fileobj,
                separators=(',', ':'),
                default=csv_serialization,
            )
        elif self.file_format == 'pickle':
            pickle.dump(list(self), fileobj, 2)
        else:
            raise NotImplementedError('Unknown format: ' + repr(self.file_format))

    def sync(self, filename):
        """ Write dict to disk """
        tempname = filename + '.tmp'
        fileobj = open(tempname, 'wb' if self.file_format == 'pickle' else 'w')
        try:
            self.dump(fileobj)
        except Exception:
            os.remove(tempname)
            logging.exception()
            return
        finally:
            fileobj.close()
        file_path = os.path.join(self.home_dir, filename)
        shutil.move(tempname, file_path)    # atomic commit
        if self.mode is not None:
            os.chmod(filename, self.mode)
