import unittest



def suite():
    from dprofiling.tests.backends import db

    suite = unittest.TestSuite()
    suite.addTests(db.suite())
    return suite

