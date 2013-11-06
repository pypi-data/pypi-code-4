#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Helper utilities to manipulate Durus databases"""
from notmm.dbapi.orm import schevo_compat

__all__ = ['open_database']

def open_database(dbname='blogs'):
    """Open and return a pointer to a Schevo Version2 database"""
    #print "open_database: opening database %s" % dbname
    assert isinstance(dbname, str), 'dbname must be a str type!'
    db = schevo_compat.XdserverProxy(dbname)
    return db
