import unittest

from ryser.graphs import symmetric_latin_graph

##########################################
# Testing of symmetric_latin_graph
##########################################

size = 1
G1 = symmetric_latin_graph(size)

size = 2
G2 = symmetric_latin_graph(size)

size = 3
G3 = symmetric_latin_graph(size)

size = 5
G5 = symmetric_latin_graph(size)

class TestSymmetricLatinGraph(unittest.TestCase):
    def test_symmetric_latin_graph(self):
        self.assertEqual( G1.order(), 1 )
        self.assertEqual( G1.size(), 0 )
        self.assertEqual( G2.order(), 3 )
        self.assertEqual( G2.size(), 2 )
        self.assertEqual( G3.order(), 6 )
        self.assertEqual( G3.size(), 9 )
        self.assertEqual( G5.order(), 15 )
        self.assertEqual( G5.size(), 50 )
