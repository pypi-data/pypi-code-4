
from unittest import TestCase

from rattail.db import core
from sqlalchemy import Column


class TestCore(TestCase):

    def test_uuid_column(self):
        column = core.uuid_column()
        self.assertIsInstance(column, Column)
        self.assertEqual(column.name, None)
        self.assertTrue(column.primary_key)
        self.assertFalse(column.nullable)
        self.assertIsNotNone(column.default)

    def test_uuid_column_no_default(self):
        column = core.uuid_column(default=None)
        self.assertIsNone(column.default)

    def test_uuid_column_nullable(self):
        column = core.uuid_column(nullable=True)
        self.assertTrue(column.nullable)
