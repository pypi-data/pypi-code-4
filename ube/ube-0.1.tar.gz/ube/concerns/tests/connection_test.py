'''
Created on Nov 6, 2012

@author: Nicklas Boerjesson
'''
import unittest
from qal.dal.tests.framework import default_dal
from ube.concerns.connection import set_connection, connection

from qal.dal.dal_types import DB_POSTGRESQL



'''The tests are only run towards one database backend, default is Postgres, 
to run against any other backend, simply change the database type in the default_dal decorator. 
With regards to the SQL, add the rather silly "FROM sysibm.sysdummy1" for DB2 and "FROM DUAL;" for Oracle.'''

test_sql = 'SELECT 1' # Doesn't work with all backends.     


@default_dal(DB_POSTGRESQL)
class concern_connection_tests(unittest.TestCase):
    _dal = None

    def setUp(self):
        set_connection(self._dal)

    def tearDown(self):
        #self._dal.close()
        pass
        
    @connection
    def test_function_connection(self, _connection = None):
        _connection.execute(test_sql)


    def test_class_connection(self, _connection = None):
        ''' This import has to be done here and the decorated class has to be in a separate module. 
        For some stupid reason, the decorator is called on import.'''
        from .connection_check_c import connection_check_class
        test_class = connection_check_class()
        test_class.connection_check(test_sql)




if __name__ == "__main__":
    #import sys;sys.argv = ['', 'Test.testName']
    unittest.main()
    

