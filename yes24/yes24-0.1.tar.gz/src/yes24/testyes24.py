# -*- coding: utf-8 -*-

'''unittest for yes24 api'''


from __future__ import print_function, unicode_literals
from yes24 import Yes24
import unittest


class TestYes24(unittest.TestCase):
	def setUp(self):
		self.yes24 = Yes24(783045)

	def tearDown(self):
		pass

	def testTitle(self):
		title = self.yes24.title
		self.assertEqual(title, 'Corvette Fifty Years')
	
	def testAuthor(self):
		author = self.yes24.author
		self.assertEqual(author, 'Randy Leffingwell | Motorbooks International')
		
	def testPrice(self):
		price = self.yes24.price
		self.assertEqual(price, '67,800원')
		
	def testDate(self):
		date = self.yes24.date
		self.assertEqual(date, '2002년 10월 01일')
		
	def testPages(self):
		pages = self.yes24.pages
		self.assertEqual(pages, '383쪽')
		
	def testPages(self):
		weight = self.yes24.weight
		self.assertEqual(weight, '2980g')
		
	def testPages(self):
		size = self.yes24.size
		self.assertEqual(size, '310*40mm')
		
	def testUrl(self):
		size = self.yes24.url
		self.assertEqual(size, 'http://www.yes24.com/24/goods/783045')
		
if __name__ == '__main__':
	unittest.main()