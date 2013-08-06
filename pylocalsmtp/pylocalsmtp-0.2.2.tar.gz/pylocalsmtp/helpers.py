from peewee import SqliteDatabase
from .settings import *


DB = SqliteDatabase(DB_NAME)
