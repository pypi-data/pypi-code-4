#coding: utf-8
__docformat__="epytext"

import wae.pdo
import redis
from wae.config import config

def connect_db():
    """连接PostgreSQL数据库"""
    dbconn = wae.pdo.connect(
        host=config.get('db', 'host'),
        port=config.getint('db', 'port', 5432),
        user=config.get('db', 'user', 'dba'),
        password=config.get('db', 'password'),
        dbname=config.get('db', 'dbname')
    )
    enc = config.get('db', 'charset')
    if enc!="":
        dbconn.execute("set client_encoding to %s" % enc)
    return dbconn


def connect_mongodb():
    """连接MongoDB数据库"""
    import pymongo
    global _mg_conns
    host = config.get('mongodb', 'host', 'localhost')
    port = config.getint('mongodb', 'port', 27017)
    k = (host, port)
    if k not in _mg_conns:
        c = pymongo.Connection(host=host, port=port)
        _mg_conns[k] = c
    return _mg_conns[k]


def connect_redis():
    """链接redis"""
    import redis
    global _redis_conn_pool
    host = config.get('redis', 'host', 'localhost')
    port = config.getint('redis', 'port', 6379)
    k = (host, port)
    if k not in _redis_conn_pool:
        cp = redis.ConnectionPool(host=host, port=port)
        _redis_conn_pool[k] = cp
    else:
        cp = _redis_conn_pool[k]
    return redis.Redis(connection_pool=cp)


def connect_mq(callback=None):
    import pika
    cred = pika.PlainCredentials(config.get('mq', 'user'), config.get('mq', 'password'))
    params = pika.ConnectionParameters(
            host = config.get('mq', 'host', 'localhost'),
            port = config.getint('mq', 'port'),
            virtual_host = config.get('mq', 'vhost'),
            credentials = cred
    )

    if callback!=None:
        mqconn=pika.AsyncoreConnection(parameters=params, on_open_callback=callback)
    else:
        mqconn=pika.BlockingConnection(params)

    return mqconn


_mg_conns = {}
_redis_conn_pool = {}

