#-*- coding: utf-8 -*-

__author__ = 'Jefurry <jefurry@qq.com>'

import sys
reload(sys)
sys.setdefaultencoding('utf-8')
sys.path.append('../../pyar')

import unittest, pyar

# MySQLdb.escape_string(name)

pyar.settings.DNS = {
    'default' : 'mysql://root:@localhost:3306/test_pyar?use_unicode=0&charset=utf8&mincached=20&maxcached=100&blocking=1&maxusage=1000&setsession=&maxconnections=1000&maxshared=0',
}

class Connection(pyar.Model):
    _debug_       =     True
    _auto_commit_ = True
    _using_       = 'default'
    _primary_key_ = 'id'
    _db_name_     = None
    _tb_name_     = None

class TestPyar(Connection):
    #_db_name_ = 'test_pyar'
    _db_name_  = lambda self, db_key: 'test_pyar'

class UserTable(TestPyar):
    #_tb_name_ = 'user'
    _tb_name_  = lambda self, tb_key: 'user'

class PyARTestCase(unittest.TestCase):
    def setUp(self):
        with UserTable() as t:
            #t.use('db_key', 'tb_key')
            w = ((pyar.F.id == 2) & (pyar.F.name == '板蓝根'))
            sql = t.qs.where(w).select(pyar.F.id)
	    #print t.first(sql) | None

    def test_insert(self):
        with UserTable() as t:
            sql = t.qs.insert(dict(enable=1,
                                   name='也伤心嗯',
                                   password='886',
                                   ctime=123456,
                                   mtime=123456))
            t.insert(sql)

    def test_update(self):
        with UserTable() as t:
            sql = t.qs.where(pyar.F.password == '886').update(dict(name='也吧'))
            t.update(sql)

    def test_delete(self):
        with UserTable() as t:
            sql = t.qs.where(pyar.F.password == '886').delete()
            t.delete(sql)

    def test_something(self):
        self.assertEqual(True, True)


if __name__ == '__main__':
    unittest.main()
