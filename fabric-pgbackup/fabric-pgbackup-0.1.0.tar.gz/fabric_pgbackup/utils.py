#!/usr/bin/env python
# -*- coding: utf-8 -*-


def is_remote(config):
    if config.get('SSH').get('SOURCE'):
        return True
    return False


def db_handle():
    """
    """
    pass


def file_handle(filepath):
    """

    """
    pass


def backup(gzip=True, split_chunks=500, with_owner=True):
    pass
