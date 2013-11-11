
from settings import settings

import motor



class DBProxy(object):

    def __init__(self):
        self.db = motor.MotorClient(
            settings['db'].get('host','localhost'),
            settings['db'].get('port', 27017)).open_sync()[settings['db']['name']]


    def find(self, collection, *args, **kwargs):
        return motor.Op(self.db[collection].find(*args, **kwargs).to_list)

    def find_one(self, collection, *args, **kwargs):
        return motor.Op(self.db[collection].find_one, *args, **kwargs)


