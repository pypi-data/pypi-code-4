#:coding=utf8:

from unittest import TestCase

from decimal import Decimal

from beproud.utils.dbutils.mysql import *

class TestMySQLCursor(TestCase):
    u"""
    DB: dbutils_test

    MySQL データベースは必須
    CREATE DATABASE bputils_test CHARACTER SET utf8;
    CREATE TABLE person (name CHAR(20) CHARACTER SET utf8 COLLATE utf8_bin);
    INSERT INTO person (name) VALUES ('ian');
    INSERT INTO person (name) VALUES ('tokibito');
    INSERT INTO person (name) VALUES ('aodag');
    """
    def setUp(self):
        self.conn = MySQLConnection({"host":"localhost", "user":"root", "db":"bputils_test", "charset":"utf8"}) 

    def test_iteration(self):
        cursor = MySQLCursor(self.conn)
        cursor.query("SELECT * from person")
        for row in cursor:
            self.assertTrue(row["name"])

    def test_iteration2(self):
        cursor = MySQLCursor(self.conn, rows=2)
        cursor.query("SELECT * from person")
        for row in cursor:
            self.assertTrue(row["name"])

    def test_restart(self):
        cursor = MySQLCursor(self.conn)
        cursor.query("SELECT * from person")

        self.assertTrue(cursor.next()["name"])
        self.assertTrue(cursor.next()["name"])
        self.assertTrue(cursor.next()["name"])

        cursor.query("SELECT * from person")
        self.assertTrue(cursor.next()["name"])
        self.assertTrue(cursor.next()["name"])
        self.assertTrue(cursor.next()["name"])

