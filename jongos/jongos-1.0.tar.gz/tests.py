from jongos import jongos
import unittest
import os
import time
from datetime import datetime

class TestBasicFunctionality(unittest.TestCase):
    def setUp(self):
	    self.db = jongos()
    
    def testInsert(self):
        self.assertIsNotNone(self.db.insert({"name": "one", "email": "one@mailinator.com"}))

    def testUpdate(self):
        self.assertIsNotNone(self.db.update({"name": "one"}, {'$set': {"email": "one@mailinator.com"}}))

    def testRemove(self):
        self.db.insert({"name": "two", "email": "two@mailinator.com"})
        self.assertIsNotNone(self.db.remove({"name": "two"}))

    
    def testFind(self):
        self.assertIsNotNone(self.db.find({"name":"one"}))

    def testGetAll(self):
        self.assertIsNotNone(self.db.find({"name":"one"}).all({'email':1}))
    
    def testFindCount(self):
        self.assertIsNotNone(self.db.find().count())
    
    def testOrderBy(self):
        self.assertIsNotNone(self.db.find().orderby())

    def testGroupBy(self):
        self.assertIsNotNone(self.db.find().groupby("name"))

    def testCount(self):
        self.assertIsNotNone(self.db.count({}))

    def testStats(self):
        self.assertIsNotNone(self.db.stats())


if __name__ == '__main__':
    unittest.main()
