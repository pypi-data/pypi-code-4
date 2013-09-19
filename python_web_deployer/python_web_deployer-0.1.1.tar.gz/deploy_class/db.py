#-*- coding: utf-8 -*-
from deploy_class.globals import NotOveroadedError
class AbstractSSHDatabaseInterface:
    def __init__(self, user, password, database, executor):
        self.user = user
        self.password = password
        self.database = database
        self.executor = executor
        
    def get_dump(self):
        """Getting DB dump"""
        raise NotOveroadedError

class MySQLSSHInterface(AbstractSSHDatabaseInterface):
    def get_dump(self):
        return self.executor.execute("mysqldump -u %(user)s -p%(pass)s %(db)s;"%{"user": self.user,
                                                                                 "pass": self.password,
                                                                                 "db": self.database})     
