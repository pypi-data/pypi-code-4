import sqlite3

from Databases.Database import Database

class SQLiteDatabase(Database):
    def __init__(self, connection, filename):
        super().__init__(connection or sqlite3.connect(filename))