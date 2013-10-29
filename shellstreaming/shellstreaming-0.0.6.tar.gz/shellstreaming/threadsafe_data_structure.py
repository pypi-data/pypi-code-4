# -*- coding: utf-8 -*-
"""
    shellstreaming.threadsafe_data_structure
    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
"""
from threading import Lock


class ThreadSafeList(object):
    def __init__(self):
        self._l = []

    def append(self, obj):
        Lock.aquire()
        self._l.append(obj)
        Lock.release()

    def pop(self, index=-1):
        Lock.aquire()
        try:
            if index == -1:
                obj = self._l.pop()
            else:
                obj = self._l.pop(index)
        finally:
            Lock.release()
        return obj

    def __delitem__(self, index):
        Lock.aquire()
        try:
            del self._l[index]
        finally:
            Lock.release()

    def __len__(self):
        Lock.aquire()
        l = len(self._l)
        Lock.release()
        return l

    def __iter__(self):
        return self

    def next(self):
        スレッドセーフな構造をiterateする方が無茶(最初から最後までのイテレーションが終わるまで外部スレッドによるupdateを許さない)
