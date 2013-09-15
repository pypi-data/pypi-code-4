from peewee_paginator.pagination import Paginator, Page
from peewee import *
from peewee import SelectQuery

import unittest

class Entry(Model):
	name = CharField()
	class Meta:
		database = SqliteDatabase(':memory:')

class PaginatorTest(unittest.TestCase):
	@classmethod
	def setUpClass(self):
		Entry.create_table()
		for i in range(1,33):
			Entry.create(name='Entry #' + str(i))
	
		query = Entry.select()
		self.paginator = Paginator(query, per_page=5)

	#Should return the count of objects in the paginator
	def test_count_method(self):
		#Should return an integer
		n = self.paginator.obj_count
		self.assertIsInstance(n, int)

		#Should be the right number
		self.assertEquals(n, 32)

	#Test the pages method
	def test_pages_method(self):
		#Should return an int
		n = self.paginator.nb_pages
		self.assertIsInstance(n, int)

		#Should calculate the righ number of pages
		self.assertEquals(n, 7)

	def test_page_method(self):
		page = self.paginator.page(1)
		self.assertIsInstance(page, Page)

		#Test that the page has a paginator associated with it
		self.assertIsInstance(page.paginator, Paginator)

		#Test that the page has its number as attribute
		self.assertIsInstance(page.num, int)
		self.assertEquals(page.num, 1)

		#Test that the page has the total number of pages as attribute
		self.assertIsInstance(page.total_pages, int)
		self.assertEquals(page.total_pages, 7)

		#Test that the next_page functions returns int
		next = page.next_page()
		self.assertIsInstance(next, int)
		self.assertEquals(next, 2)

		#Test that it returns false if no next page
		next2 = self.paginator.page(7).next_page()
		self.assertEquals(next2, False)

		#Test the previous_page() method
		prev = page.previous_page()
		self.assertEquals(prev, False)

		prev = self.paginator.page(7).previous_page()
		self.assertIsInstance(prev, int)
		self.assertEquals(prev, 6)

		#Test the objects method of Page class
		objs = page.objects()
		self.assertIsInstance(objs, SelectQuery) #To review...



