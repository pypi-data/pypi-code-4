from unittest import TestCase


class Layer(object):

	__name__ = 'Layer'
	__bases__ = ()

	def setUp(self):
		pass

	def tearDown(self):
		raise Exception('Gaaa!')


class TestTearDown(TestCase):

	layer = Layer()

	def testFoo(self):
		pass
