from pymongo import MongoClient
import datetime

MONGO_SETTING = {}

def setup (db_ip='localhost', db_port=27017, db_name='mydb'):
    MONGO_SETTING['host'] = db_ip
    MONGO_SETTING['port'] = db_port
    MONGO_SETTING['db'] = db_name

def get_db ():
    """
    db = client.movs
    collection = db.movies
    """
    client = MongoClient (MONGO_SETTING['host'], 
                          MONGO_SETTING['port'])
    return client[MONGO_SETTING['db']]

